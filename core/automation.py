from datetime import timedelta

from django.utils import timezone

from .models import ActivityEntry, AutomationRule, Profile, Project, Task
from .notifications import notify_profiles, send_notification_email
from .utils import log_activity


def _profile_emails(profiles):
    emails = []
    for profile in profiles:
        user = getattr(profile, "user", None)
        email = getattr(user, "email", None)
        if email:
            emails.append(email)
    return emails


def _dedupe_profiles(profiles):
    seen = set()
    unique = []
    for profile in profiles:
        if not profile or profile.id in seen:
            continue
        seen.add(profile.id)
        unique.append(profile)
    return unique


def _already_reminded(task, event_type):
    return ActivityEntry.objects.filter(
        event_type=event_type,
        task=task,
        metadata__due_date=str(task.due_date),
    ).exists()


def _notify_task(task, subject, message, event_type, severity, days, dry_run):
    if _already_reminded(task, event_type):
        return {"skipped": 1}
    assignees = list(task.assignees.select_related("user"))
    recipients = _profile_emails(assignees)
    if not recipients:
        return {"no_recipients": 1}
    if not dry_run:
        send_notification_email(subject, message, recipients)
        notify_profiles(
            assignees,
            subject,
            message,
            notification_type=event_type,
            severity=severity,
            project=task.project,
            task=task,
            metadata={"due_date": str(task.due_date), "days": days},
            preference_key="task_assigned",
        )
        log_activity(
            event_type,
            subject,
            description=message[:200],
            severity=severity,
            task=task,
            project=task.project,
            metadata={"due_date": str(task.due_date), "days": days},
        )
    return {"tasks_notified": 1, "emails_sent": len(recipients)}


def send_task_reminders(days=3, include_overdue=True, include_due_soon=True, dry_run=False):
    today = timezone.now().date()
    end = today + timedelta(days=days)
    summary = {
        "tasks_due_soon": 0,
        "tasks_overdue": 0,
        "tasks_notified": 0,
        "emails_sent": 0,
        "skipped": 0,
        "no_recipients": 0,
    }

    base_qs = (
        Task.objects.select_related("project")
        .prefetch_related("assignees__user")
        .filter(is_archived=False)
        .exclude(status="DONE")
    )

    if include_due_soon and days > 0:
        due_soon = base_qs.filter(due_date__isnull=False, due_date__gte=today, due_date__lte=end)
        summary["tasks_due_soon"] = due_soon.count()
        for task in due_soon:
            result = _notify_task(
                task,
                f"Task reminder: {task.title}",
                f"Task is due on {task.due_date}.",
                "task_reminder_due_soon",
                "WARNING",
                days,
                dry_run,
            )
            for key, value in result.items():
                summary[key] += value

    if include_overdue:
        overdue = base_qs.filter(due_date__isnull=False, due_date__lt=today)
        summary["tasks_overdue"] = overdue.count()
        for task in overdue:
            result = _notify_task(
                task,
                f"Task overdue: {task.title}",
                f"Task was due on {task.due_date}. Please update the status.",
                "task_reminder_overdue",
                "DANGER",
                days,
                dry_run,
            )
            for key, value in result.items():
                summary[key] += value

    return summary


def _rule_recipients(rule, task):
    if rule.action != "NOTIFY":
        return []
    config = rule.config or {}
    recipient_ids = config.get("recipient_ids") or []
    if recipient_ids:
        return _dedupe_profiles(
            [p for p in task.assignees.all() if p.id in recipient_ids]
            + [p for p in task.stakeholders.all() if p.id in recipient_ids]
        )
    if config.get("notify_assignees", True):
        return _dedupe_profiles(task.assignees.all())
    if config.get("notify_stakeholders"):
        return _dedupe_profiles(task.stakeholders.all())
    return []


def _project_rule_recipients(rule, project):
    if rule.action != "NOTIFY":
        return []
    config = rule.config or {}
    recipient_ids = config.get("recipient_ids") or []
    recipients = []
    if recipient_ids:
        recipients.extend([p for p in project.owners.all() if p.id in recipient_ids])
        recipients.extend([p for p in project.participants.all() if p.id in recipient_ids])
        return _dedupe_profiles(recipients)
    if config.get("notify_owners", True):
        recipients.extend(project.owners.all())
    if config.get("notify_participants", True):
        recipients.extend(project.participants.all())
    return _dedupe_profiles(recipients)


def _run_automation_rule(rule, task, actor=None):
    if not rule.is_active:
        return None
    action = rule.action
    config = rule.config or {}
    if action == "NOTIFY":
        recipients = _rule_recipients(rule, task)
        if not recipients:
            return None
        emails = _profile_emails(recipients)
        if not emails:
            return None
        subject = config.get("subject") or f"Automatisierte Benachrichtigung: {task.title}"
        message = config.get("message") or f"Die Task \"{task.title}\" hat einen neuen Status: {task.status}."
        send_notification_email(subject, message, emails)
        notify_profiles(
            recipients,
            subject,
            message,
            notification_type="automation_notification",
            actor=actor,
            severity="INFO",
            project=task.project,
            task=task,
            metadata={"rule": rule.name, "action": action},
            preference_key="task_assigned",
        )
        log_activity(
            "automation_notification",
            subject,
            description=message[:200],
            actor=actor,
            severity="INFO",
            task=task,
            project=task.project,
            metadata={"rule": rule.name, "action": action},
        )
    elif action == "ASSIGN":
        assignee_id = config.get("assignee_id")
        if assignee_id:
            try:
                assignee = Profile.objects.get(id=assignee_id)
            except Profile.DoesNotExist:
                assignee = None
            if assignee and not task.assignees.filter(id=assignee.id).exists():
                task.assignees.add(assignee)
                log_activity(
                    "automation_assign",
                    f"Automatischer Assignee: {assignee.name or assignee.user.username}",
                    actor=actor,
                    severity="INFO",
                    task=task,
                    project=task.project,
                    metadata={"rule": rule.name},
                )
    elif action == "WEBHOOK":
        log_activity(
            "automation_webhook",
            f"Webhook ausgelöst: {rule.name}",
            actor=actor,
            severity="INFO",
            task=task,
            project=task.project,
            metadata={"rule": rule.name, "config": config},
        )
    return True


def run_automation_rules_for_task(task, event_type, actor=None):
    if event_type not in {"TASK_STATUS", "TASK_DUE"}:
        return
    rules = AutomationRule.objects.filter(trigger=event_type, is_active=True)
    for rule in rules:
        _run_automation_rule(rule, task, actor=actor)


def _run_project_automation_rule(rule, project, actor=None):
    if not rule.is_active:
        return None
    action = rule.action
    config = rule.config or {}
    if action == "NOTIFY":
        recipients = _project_rule_recipients(rule, project)
        if not recipients:
            return None
        emails = _profile_emails(recipients)
        if not emails:
            return None
        subject = config.get("subject") or f"Automatisierte Projekt-Benachrichtigung: {project.title}"
        message = config.get("message") or f"Das Projekt \"{project.title}\" hat einen neuen Status: {project.status}."
        send_notification_email(subject, message, emails)
        notify_profiles(
            recipients,
            subject,
            message,
            notification_type="automation_notification",
            actor=actor,
            severity="INFO",
            project=project,
            metadata={"rule": rule.name, "action": action},
            preference_key="project_updates",
        )
        log_activity(
            "automation_notification",
            subject,
            description=message[:200],
            actor=actor,
            severity="INFO",
            project=project,
            metadata={"rule": rule.name, "action": action},
        )
    elif action == "ASSIGN":
        participant_id = config.get("participant_id") or config.get("assignee_id")
        owner_id = config.get("owner_id")
        changed = False
        if participant_id:
            try:
                participant = Profile.objects.get(id=participant_id)
            except Profile.DoesNotExist:
                participant = None
            if participant and not project.participants.filter(id=participant.id).exists():
                project.participants.add(participant)
                changed = True
        if owner_id:
            try:
                owner = Profile.objects.get(id=owner_id)
            except Profile.DoesNotExist:
                owner = None
            if owner and not project.owners.filter(id=owner.id).exists():
                project.owners.add(owner)
                changed = True
        if changed:
            log_activity(
                "automation_assign",
                f"Automatische Projektzuweisung: {project.title}",
                actor=actor,
                severity="INFO",
                project=project,
                metadata={"rule": rule.name},
            )
    elif action == "WEBHOOK":
        log_activity(
            "automation_webhook",
            f"Webhook ausgelöst: {rule.name}",
            actor=actor,
            severity="INFO",
            project=project,
            metadata={"rule": rule.name, "config": config},
        )
    return True


def run_automation_rules_for_project(project, event_type, actor=None):
    if event_type != "PROJECT_STATUS" or not isinstance(project, Project):
        return
    rules = AutomationRule.objects.filter(trigger=event_type, is_active=True)
    for rule in rules:
        _run_project_automation_rule(rule, project, actor=actor)

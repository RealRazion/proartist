from datetime import timedelta
import json

from django.utils import timezone

from .models import ActivityEntry, AutomationRule, Profile, Task
from .notifications import send_notification_email
from .utils import log_activity


def _profile_emails(profiles):
    emails = []
    for profile in profiles:
        user = getattr(profile, "user", None)
        email = getattr(user, "email", None)
        if email:
            emails.append(email)
    return emails


def _already_reminded(task, event_type):
    return ActivityEntry.objects.filter(
        event_type=event_type,
        task=task,
        metadata__due_date=str(task.due_date),
    ).exists()


def _notify_task(task, subject, message, event_type, severity, days, dry_run):
    if _already_reminded(task, event_type):
        return {"skipped": 1}
    recipients = _profile_emails(task.assignees.select_related("user"))
    if not recipients:
        return {"no_recipients": 1}
    if not dry_run:
        send_notification_email(subject, message, recipients)
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
        return [p for p in task.assignees.all() if p.id in recipient_ids] + [p for p in task.stakeholders.all() if p.id in recipient_ids]
    if config.get("notify_assignees", True):
        return list(task.assignees.all())
    if config.get("notify_stakeholders"):
        return list(task.stakeholders.all())
    return []


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

from datetime import timedelta

from django.utils import timezone

from .models import ActivityEntry, Task
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

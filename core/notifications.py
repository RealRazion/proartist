from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import Notification


def send_notification_email(subject, message, recipients):
    """
    Fire-and-forget notification email helper.
    Relies on Django's configured EMAIL backend.
    """
    if not recipients:
        return
    sender = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@unyq.app")
    try:
        send_mail(subject, message, sender, recipients, fail_silently=True)
    except Exception:
        # We intentionally swallow exceptions so that UI actions do not fail because of email issues.
        pass


def _profile_allows(profile, preference_key=None):
    if not profile:
        return False
    if not preference_key:
        return True
    settings_map = getattr(profile, "notification_settings", None) or {}
    return settings_map.get(preference_key, True)


def create_in_app_notification(
    recipient,
    title,
    body="",
    *,
    notification_type="system",
    severity="INFO",
    actor=None,
    project=None,
    task=None,
    metadata=None,
    preference_key=None,
):
    if not recipient or not _profile_allows(recipient, preference_key):
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        title=title,
        body=body,
        severity=severity,
        project=project,
        task=task,
        metadata=metadata or {},
    )


def notify_profiles(
    profiles,
    title,
    body="",
    *,
    notification_type="system",
    severity="INFO",
    actor=None,
    project=None,
    task=None,
    metadata=None,
    preference_key=None,
    mark_read=False,
):
    created = []
    seen = set()
    for profile in profiles or []:
        if not profile or profile.id in seen:
            continue
        seen.add(profile.id)
        notification = create_in_app_notification(
            profile,
            title,
            body,
            notification_type=notification_type,
            severity=severity,
            actor=actor,
            project=project,
            task=task,
            metadata=metadata,
            preference_key=preference_key,
        )
        if notification and mark_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        if notification:
            created.append(notification)
    return created

from django.conf import settings
from django.core.mail import send_mail


def send_notification_email(subject, message, recipients):
    """
    Fire-and-forget notification email helper.
    Relies on Django's configured EMAIL backend.
    """
    if not recipients:
        return
    sender = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@proartist.app")
    try:
        send_mail(subject, message, sender, recipients, fail_silently=True)
    except Exception:
        # We intentionally swallow exceptions so that UI actions do not fail because of email issues.
        pass

from django.core.management.base import BaseCommand

from core.automation import send_growpro_reminders, send_task_reminders


class Command(BaseCommand):
    help = "Send reminder emails and notifications for tasks and GrowPro due dates."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=3)
        parser.add_argument("--dry-run", action="store_true", default=False)
        parser.add_argument("--no-overdue", action="store_true", default=False)
        parser.add_argument("--no-due-soon", action="store_true", default=False)

    def handle(self, *args, **options):
        days = max(1, min(30, options["days"]))
        task_summary = send_task_reminders(
            days=days,
            include_overdue=not options["no_overdue"],
            include_due_soon=not options["no_due_soon"],
            dry_run=options["dry_run"],
        )
        growpro_summary = send_growpro_reminders(dry_run=options["dry_run"])
        self.stdout.write(str({"days": days, "tasks": task_summary, "growpro": growpro_summary}))

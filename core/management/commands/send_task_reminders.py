from django.core.management.base import BaseCommand

from core.automation import send_task_reminders


class Command(BaseCommand):
    help = "Send task reminder emails for due soon and overdue tasks."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=3)
        parser.add_argument("--dry-run", action="store_true", default=False)
        parser.add_argument("--no-overdue", action="store_true", default=False)
        parser.add_argument("--no-due-soon", action="store_true", default=False)

    def handle(self, *args, **options):
        days = max(1, min(30, options["days"]))
        summary = send_task_reminders(
            days=days,
            include_overdue=not options["no_overdue"],
            include_due_soon=not options["no_due_soon"],
            dry_run=options["dry_run"],
        )
        self.stdout.write(str(summary))

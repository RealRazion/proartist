from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_task_due_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="project",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="task",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
    ]

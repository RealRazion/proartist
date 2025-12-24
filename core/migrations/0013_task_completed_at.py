from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_profile_notification_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

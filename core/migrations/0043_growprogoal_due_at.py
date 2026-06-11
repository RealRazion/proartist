from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0042_project_color"),
    ]

    operations = [
        migrations.AddField(
            model_name="growprogoal",
            name="due_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
                help_text="Optionale Uhrzeit der Fälligkeit für präzise Erinnerungen",
            ),
        ),
    ]

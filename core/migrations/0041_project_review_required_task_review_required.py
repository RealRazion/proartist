from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0040_rankedseasonsettings_ranktierconfig_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="review_required",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="task",
            name="review_required",
            field=models.BooleanField(default=False),
        ),
    ]

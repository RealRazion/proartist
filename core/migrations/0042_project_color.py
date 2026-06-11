from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0041_project_review_required_task_review_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="color",
            field=models.CharField(default="#4f46e5", max_length=16),
        ),
    ]

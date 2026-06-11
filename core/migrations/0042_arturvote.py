from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0041_project_review_required_task_review_required"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArturVote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "choice",
                    models.CharField(
                        choices=[
                            ("pizza", "Pizza"),
                            ("pasta", "Pasta"),
                            ("currywurst_mit_pommes", "Currywurst mit Pommes"),
                            ("fish_burger", "Fish Burger"),
                            ("eigene_idee", "Eigene Idee"),
                        ],
                        max_length=32,
                    ),
                ),
                ("custom_idea", models.CharField(blank=True, default="", max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

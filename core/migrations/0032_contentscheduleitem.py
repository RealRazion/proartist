from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0031_financeentry_subscription"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContentScheduleItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scheduled_date", models.DateField(db_index=True)),
                ("platform", models.CharField(choices=[("youtube", "YouTube"), ("instagram", "Instagram"), ("tiktok", "TikTok"), ("twitter", "X / Twitter"), ("podcast", "Podcast"), ("blog", "Blog"), ("other", "Sonstiges")], default="youtube", max_length=20)),
                ("status", models.CharField(choices=[("draft", "Entwurf"), ("ready", "Bereit"), ("posted", "Gepostet")], default="draft", max_length=12)),
                ("title", models.CharField(blank=True, default="", max_length=120)),
                ("note", models.CharField(blank=True, default="", max_length=400)),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("profile", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="content_schedule_items", to="core.profile")),
            ],
            options={
                "ordering": ["scheduled_date", "sort_order", "created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="contentscheduleitem",
            index=models.Index(fields=["profile", "scheduled_date"], name="core_conten_profile_b75432_idx"),
        ),
        migrations.AddIndex(
            model_name="contentscheduleitem",
            index=models.Index(fields=["profile", "status"], name="core_conten_profile_41cddb_idx"),
        ),
    ]

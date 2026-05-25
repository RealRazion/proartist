from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0033_newspost_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournament",
            name="allow_vote_change",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="tournament",
            name="max_votes_per_ip_per_hour",
            field=models.PositiveIntegerField(default=20),
        ),
        migrations.AddField(
            model_name="tournament",
            name="min_account_age_hours",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="tournament",
            name="voting_mode",
            field=models.CharField(
                choices=[
                    ("COMMUNITY", "Community"),
                    ("HYBRID", "Hybrid (Community + Jury)"),
                    ("JURY_ONLY", "Nur Jury"),
                ],
                default="COMMUNITY",
                max_length=12,
            ),
        ),
    ]

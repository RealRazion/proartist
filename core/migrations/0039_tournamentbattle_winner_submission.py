from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0038_managedplatform_version"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentbattle",
            name="closed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tournamentbattle",
            name="winner_submission",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="won_battles",
                to="core.tournamentsubmission",
            ),
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0034_tournament_voting_settings"),
    ]

    operations = [
        migrations.AddField(
            model_name="tournamentvote",
            name="flag_reason",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="tournamentvote",
            name="is_flagged",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="tournamentvote",
            name="moderated_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tournamentvote",
            name="moderated_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="moderated_tournament_votes", to="core.profile"),
        ),
        migrations.AddField(
            model_name="tournamentvote",
            name="moderation_status",
            field=models.CharField(choices=[("APPROVED", "Freigegeben"), ("PENDING_REVIEW", "In Prüfung"), ("REJECTED", "Abgelehnt")], default="APPROVED", max_length=16),
        ),
        migrations.AddField(
            model_name="tournamentvote",
            name="voter_ip",
            field=models.CharField(blank=True, max_length=45),
        ),
        migrations.AddField(
            model_name="tournamentvote",
            name="voter_user_agent",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

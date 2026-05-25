from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0035_tournamentvote_moderation"),
    ]

    operations = [
        migrations.AddField(
            model_name="song",
            name="bpm",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="song",
            name="genre",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="song",
            name="key_signature",
            field=models.CharField(blank=True, max_length=16),
        ),
        migrations.AddField(
            model_name="song",
            name="mood",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="song",
            name="release_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="song",
            name="tags",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="songversion",
            name="duration_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]

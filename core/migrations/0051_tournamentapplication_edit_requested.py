from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_hubmusictip'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournamentapplication',
            name='edit_requested',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tournamentapplication',
            name='edit_request_message',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='tournamentapplication',
            name='edit_request_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]

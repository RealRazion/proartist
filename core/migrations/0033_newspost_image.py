from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0032_contentscheduleitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="newspost",
            name="image",
            field=models.FileField(blank=True, null=True, upload_to="news/"),
        ),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0037_managedplatform"),
    ]

    operations = [
        migrations.AddField(
            model_name="managedplatform",
            name="version",
            field=models.CharField(default="0.1", max_length=20),
        ),
    ]

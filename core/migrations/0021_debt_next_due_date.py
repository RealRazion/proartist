from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_debt"),
    ]

    operations = [
        migrations.AddField(
            model_name="debt",
            name="next_due_date",
            field=models.DateField(blank=True, help_text="Naechster Faelligkeitstermin", null=True),
        ),
    ]

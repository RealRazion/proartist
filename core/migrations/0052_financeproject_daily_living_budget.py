from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0051_tournamentapplication_edit_requested"),
    ]

    operations = [
        migrations.AddField(
            model_name="financeproject",
            name="daily_living_budget",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text="Geplantes Alltags-Tagesbudget fuer Tag-fuer-Tag Prognose",
                max_digits=12,
            ),
        ),
    ]


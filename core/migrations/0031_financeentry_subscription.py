from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0030_debtpayment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="financeentry",
            name="entry_type",
            field=models.CharField(
                choices=[
                    ("INCOME", "Einnahme"),
                    ("FIXED", "Fixkosten"),
                    ("SUBSCRIPTION", "Abo"),
                    ("VARIABLE", "Variable Ausgabe"),
                    ("DEBT", "Schuldenrate"),
                    ("SAVING", "Sparen"),
                ],
                default="FIXED",
                max_length=12,
            ),
        ),
    ]
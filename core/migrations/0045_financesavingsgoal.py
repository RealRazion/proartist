from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0044_profile_avatar_role_access_policy_and_admin_role"),
    ]

    operations = [
        migrations.CreateModel(
            name="FinanceSavingsGoal",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=160)),
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("current_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("target_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("is_completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "project",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="savings_goals", to="core.financeproject"),
                ),
            ],
            options={
                "ordering": ["is_completed", "target_date", "title", "created_at"],
            },
        ),
    ]

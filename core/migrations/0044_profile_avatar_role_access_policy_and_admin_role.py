from django.db import migrations, models
import django.db.models.deletion


def seed_roles_and_policies(apps, schema_editor):
    Role = apps.get_model("core", "Role")
    RoleAccessPolicy = apps.get_model("core", "RoleAccessPolicy")

    for key in ["ADMIN", "TEAM", "ARTIST", "MEMBER"]:
        Role.objects.get_or_create(key=key)
        RoleAccessPolicy.objects.get_or_create(role_key=key, defaults={"access_rules": {}})


def noop_reverse(apps, schema_editor):
    return


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0043_growprogoal_due_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="key",
            field=models.CharField(
                choices=[
                    ("ADMIN", "Administrator"),
                    ("TEAM", "Team/Admin"),
                    ("ARTIST", "Artist / Rapper / Sänger"),
                    ("PROD", "Producer"),
                    ("VIDEO", "Videograf"),
                    ("MERCH", "Merchandiser"),
                    ("MKT", "Vermarktung/Managing"),
                    ("LOC", "Location"),
                    ("MEMBER", "Selbst registriertes Mitglied"),
                ],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="avatar",
            field=models.ImageField(blank=True, null=True, upload_to="avatars/"),
        ),
        migrations.CreateModel(
            name="RoleAccessPolicy",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role_key", models.CharField(choices=[("ADMIN", "Administrator"), ("TEAM", "Team"), ("ARTIST", "Artist"), ("MEMBER", "Member")], max_length=20, unique=True)),
                ("access_rules", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="role_access_policy_updates",
                        to="core.profile",
                    ),
                ),
            ],
            options={"ordering": ["role_key"]},
        ),
        migrations.RunPython(seed_roles_and_policies, noop_reverse),
    ]

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_financeproject_dispo_used"),
    ]

    operations = [
        migrations.CreateModel(
            name="PluginGuideImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.FileField(upload_to="plugin_guides/gallery/")),
                ("sort_order", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("guide", models.ForeignKey(on_delete=models.deletion.CASCADE, related_name="images", to="core.pluginguide")),
            ],
            options={
                "ordering": ["sort_order", "created_at"],
            },
        ),
    ]

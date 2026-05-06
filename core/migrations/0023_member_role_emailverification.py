from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_add_savings_percentage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='key',
            field=models.CharField(
                choices=[
                    ('TEAM', 'Team/Admin'),
                    ('ARTIST', 'Artist / Rapper / Sänger'),
                    ('PROD', 'Producer'),
                    ('VIDEO', 'Videograf'),
                    ('MERCH', 'Merchandiser'),
                    ('MKT', 'Vermarktung/Managing'),
                    ('LOC', 'Location'),
                    ('MEMBER', 'Selbst registriertes Mitglied'),
                ],
                max_length=20,
                unique=True,
            ),
        ),
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('code', models.CharField(max_length=6)),
                ('description', models.TextField(blank=True)),
                ('expires_at', models.DateTimeField()),
                ('used', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]

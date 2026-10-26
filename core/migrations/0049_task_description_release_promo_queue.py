from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_album_song_cover_version_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='release',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_releases', to='core.profile'),
        ),
        migrations.AddField(
            model_name='release',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='release',
            name='notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='release',
            name='promo_model',
            field=models.CharField(default='CUSTOM', max_length=50),
        ),
        migrations.AddField(
            model_name='release',
            name='promo_plan',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='release',
            name='reminder_email_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.CreateModel(
            name='PromoQueueTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('scheduled_date', models.DateField(db_index=True)),
                ('category', models.CharField(choices=[('TIKTOK_DAILY', 'Daily TikTok / Reel'), ('COLLAB_POST', 'Collab Post'), ('SNIPPET', 'Audio Snippet Drop'), ('PRE_SAVE', 'Pre-Save Link'), ('RELEASE_DAY', 'Release Day Blast'), ('POST_PUSH', 'Post-Release Push'), ('CUSTOM', 'Individuelle Promo')], default='CUSTOM', max_length=40)),
                ('platform', models.CharField(default='TikTok', max_length=50)),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo_tasks', to='core.profile')),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo_tasks', to='core.release')),
            ],
            options={
                'ordering': ['scheduled_date', 'id'],
            },
        ),
    ]

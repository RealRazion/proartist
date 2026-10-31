from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_task_description_release_promo_queue'),
    ]

    operations = [
        migrations.CreateModel(
            name='HubMusicTip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('badge', models.CharField(default='UNYQ Music Tipp', max_length=100)),
                ('subtitle', models.CharField(default='Neuer exklusiver VIP-Drop verfügbar', max_length=250)),
                ('title', models.CharField(default='Midnight Drive in Berlin', max_length=200)),
                ('artist', models.CharField(default='KAZA & UNYQ', max_length=200)),
                ('button_text', models.CharField(default='▶ Jetzt reinhören', max_length=100)),
                ('link_url', models.CharField(default='/platforms/music', max_length=500)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='hub_music_tip_updates', to='core.profile')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
    ]

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from core.models import Profile, Role, Project, Song, SongVersion, GrowProGoal, Request


class Command(BaseCommand):
    help = "Legt einfache Demo-Daten (Profile, Song, GrowPro-Ziel, Request) an."

    def handle(self, *args, **options):
        team_role, _ = Role.objects.get_or_create(key="TEAM")
        artist_role, _ = Role.objects.get_or_create(key="ARTIST")

        team_user, _ = User.objects.get_or_create(username="demo_team", defaults={"email": "team@example.com"})
        team_user.set_password("demo1234")
        team_user.save()
        team_profile, _ = Profile.objects.get_or_create(user=team_user, defaults={"name": "Demo Team"})
        team_profile.roles.add(team_role)

        artist_user, _ = User.objects.get_or_create(username="demo_artist", defaults={"email": "artist@example.com"})
        artist_user.set_password("demo1234")
        artist_user.save()
        artist_profile, _ = Profile.objects.get_or_create(user=artist_user, defaults={"name": "Demo Artist", "city": "Berlin"})
        artist_profile.roles.add(artist_role)

        project, _ = Project.objects.get_or_create(title="Demo Projekt", defaults={"description": "Beispielprojekt"})
        project.participants.add(artist_profile)

        song, _ = Song.objects.get_or_create(profile=artist_profile, title="Demo Song", defaults={"project": project})
        SongVersion.objects.get_or_create(song=song, version_number=1, defaults={"notes": "Erste Version"})

        goal, _ = GrowProGoal.objects.get_or_create(
            profile=artist_profile,
            title="Monatliche Hörer steigern",
            defaults={
                "metric": "Hörer",
                "unit": "Hörer",
                "target_value": 50000,
                "current_value": 10000,
                "due_date": timezone.now().date(),
                "created_by": team_profile,
            },
        )

        Request.objects.get_or_create(
            sender=artist_profile,
            receiver=team_profile,
            defaults={"req_type": "COLLAB", "message": "Lass uns zusammenarbeiten"},
        )

        self.stdout.write(self.style.SUCCESS("Demo-Daten angelegt."))

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Booking, Event, Profile, Role


class BookingAccessApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.team_role, _ = Role.objects.get_or_create(key="TEAM")
        self.artist_role, _ = Role.objects.get_or_create(key="ARTIST")

        self.team_user = User.objects.create_user(username="team-booking", password="pw123456")
        self.team_profile = Profile.objects.create(user=self.team_user, name="Team Booking")
        self.team_profile.roles.add(self.team_role)

        self.artist_user = User.objects.create_user(username="artist-booking", password="pw123456")
        self.artist_profile = Profile.objects.create(user=self.artist_user, name="Artist Booking")
        self.artist_profile.roles.add(self.artist_role)

        self.other_user = User.objects.create_user(username="artist-other", password="pw123456")
        self.other_profile = Profile.objects.create(user=self.other_user, name="Artist Other")
        self.other_profile.roles.add(self.artist_role)

        self.event = Event.objects.create(
            title="Test Event",
            date=date(2026, 5, 20),
            location="Berlin",
            fee_total="1000.00",
        )

    def test_non_team_user_only_sees_own_bookings(self):
        Booking.objects.create(event=self.event, profile=self.artist_profile, slot_time="20:00")
        Booking.objects.create(event=self.event, profile=self.other_profile, slot_time="21:00")

        self.client.force_authenticate(user=self.artist_user)
        res = self.client.get("/api/bookings/")

        self.assertEqual(res.status_code, 200, res.content)
        payload = res.json()
        results = payload.get("results", payload)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["profile"], self.artist_profile.id)

    def test_non_team_create_forces_own_profile(self):
        self.client.force_authenticate(user=self.artist_user)

        res = self.client.post(
            "/api/bookings/",
            {
                "event": self.event.id,
                "profile": self.other_profile.id,
                "slot_time": "22:00",
                "payout_amount": "250.00",
                "status": "APPLIED",
            },
            format="json",
        )

        self.assertEqual(res.status_code, 201, res.content)
        booking = Booking.objects.get(id=res.json()["id"])
        self.assertEqual(booking.profile_id, self.artist_profile.id)

    def test_team_user_sees_all_bookings(self):
        Booking.objects.create(event=self.event, profile=self.artist_profile, slot_time="20:00")
        Booking.objects.create(event=self.event, profile=self.other_profile, slot_time="21:00")

        self.client.force_authenticate(user=self.team_user)
        res = self.client.get("/api/bookings/")

        self.assertEqual(res.status_code, 200, res.content)
        payload = res.json()
        results = payload.get("results", payload)
        self.assertEqual(len(results), 2)

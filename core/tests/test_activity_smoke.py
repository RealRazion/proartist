from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from core.models import Profile, Role, ActivityEntry


class ActivityFeedSmokeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        team_role, _ = Role.objects.get_or_create(key="TEAM")
        user = User.objects.create_user(username="teamuser", password="pw123456")
        self.profile = Profile.objects.create(user=user, name="Team")
        self.profile.roles.add(team_role)
        ActivityEntry.objects.create(event_type="test", title="Hello")
        self.client.force_login(user)

    def test_activity_feed_returns_entries(self):
        res = self.client.get("/activity/")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json()) >= 1)

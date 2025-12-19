from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from core.models import Profile, Role
from core.serializers import ProfileSerializer


class ProfileSerializerTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="secret", email="tester@example.com")
        self.profile = Profile.objects.create(user=self.user, name="Tester")
        self.factory = APIRequestFactory()

    def test_partial_update_without_role_ids(self):
        request = self.factory.put("/api/profiles/")
        request.user = self.user
        serializer = ProfileSerializer(
            instance=self.profile,
            data={"name": "Updated Name"},
            partial=True,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.name, "Updated Name")

    def test_role_assignment_strips_team_for_non_team_user(self):
        team_role = Role.objects.create(key="TEAM")
        request = self.factory.put("/api/profiles/")
        request.user = self.user
        serializer = ProfileSerializer(
            instance=self.profile,
            data={"role_ids": [team_role.id]},
            partial=True,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        serializer.save()
        self.assertFalse(self.profile.roles.filter(key="TEAM").exists())

    def test_notification_settings_saved(self):
        request = self.factory.put("/api/profiles/")
        request.user = self.user
        serializer = ProfileSerializer(
            instance=self.profile,
            data={"notification_settings": {"task_assigned": False, "digest": True}},
            partial=True,
            context={"request": request},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        instance = serializer.save()
        self.assertEqual(instance.notification_settings.get("task_assigned"), False)
        self.assertEqual(instance.notification_settings.get("digest"), True)

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import ActivityEntry, ManagedPlatform, Profile, Role


class ManagePlatformsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.team_role, _ = Role.objects.get_or_create(key="TEAM")
        self.artist_role, _ = Role.objects.get_or_create(key="ARTIST")

        self.team_user = User.objects.create_user(username="team-platform", password="pw123456")
        self.team_profile = Profile.objects.create(user=self.team_user, name="Team Platform")
        self.team_profile.roles.add(self.team_role)

        self.artist_user = User.objects.create_user(username="artist-platform", password="pw123456")
        self.artist_profile = Profile.objects.create(user=self.artist_user, name="Artist Platform")
        self.artist_profile.roles.add(self.artist_role)

    def test_team_can_create_and_update_managed_platform(self):
        self.client.force_authenticate(user=self.team_user)

        create_res = self.client.post(
            "/api/manage-platforms/",
            {
                "name": "Finance",
                "slug": "finance",
                "status": "ACTIVE",
                "allow_non_team_users": True,
                "status_note": "Alles stabil",
            },
            format="json",
        )
        self.assertEqual(create_res.status_code, 201, create_res.content)

        platform = ManagedPlatform.objects.get(id=create_res.json()["id"])
        self.assertEqual(platform.updated_by_id, self.team_profile.id)
        self.assertEqual(platform.version, "0.1")

        update_res = self.client.patch(
            f"/api/manage-platforms/{platform.id}/",
            {"status": "MAINTENANCE", "status_note": "Kurz offline"},
            format="json",
        )
        self.assertEqual(update_res.status_code, 200, update_res.content)

        platform.refresh_from_db()
        self.assertEqual(platform.status, "MAINTENANCE")
        self.assertEqual(platform.status_note, "Kurz offline")
        self.assertEqual(platform.version, "0.2")

    def test_non_team_cannot_manage_platforms(self):
        self.client.force_authenticate(user=self.artist_user)

        create_res = self.client.post(
            "/api/manage-platforms/",
            {
                "name": "Bookings",
                "slug": "bookings",
                "status": "ACTIVE",
                "allow_non_team_users": True,
            },
            format="json",
        )
        self.assertEqual(create_res.status_code, 403, create_res.content)

        list_res = self.client.get("/api/manage-platforms/")
        self.assertEqual(list_res.status_code, 403, list_res.content)

    def test_access_state_reflects_status_for_team_and_non_team(self):
        ManagedPlatform.objects.create(
            name="Finance",
            slug="finance",
            status="ACTIVE",
            allow_non_team_users=True,
        )
        ManagedPlatform.objects.create(
            name="Bookings",
            slug="bookings",
            status="ACTIVE",
            allow_non_team_users=False,
        )
        ManagedPlatform.objects.create(
            name="Analytics",
            slug="analytics",
            status="MAINTENANCE",
            allow_non_team_users=True,
        )
        ManagedPlatform.objects.create(
            name="Support",
            slug="support",
            status="LOCKED",
            allow_non_team_users=True,
        )

        self.client.force_authenticate(user=self.artist_user)
        artist_res = self.client.get("/api/manage-platforms/access-state/")
        self.assertEqual(artist_res.status_code, 200, artist_res.content)
        artist_rows = {row["slug"]: row for row in artist_res.json()}

        self.assertTrue(artist_rows["finance"]["is_accessible"])
        self.assertFalse(artist_rows["bookings"]["is_accessible"])
        self.assertFalse(artist_rows["analytics"]["is_accessible"])
        self.assertFalse(artist_rows["support"]["is_accessible"])

        self.client.force_authenticate(user=self.team_user)
        team_res = self.client.get("/api/manage-platforms/access-state/")
        self.assertEqual(team_res.status_code, 200, team_res.content)
        team_rows = {row["slug"]: row for row in team_res.json()}

        self.assertTrue(team_rows["finance"]["is_accessible"])
        self.assertTrue(team_rows["bookings"]["is_accessible"])
        self.assertTrue(team_rows["analytics"]["is_accessible"])
        self.assertFalse(team_rows["support"]["is_accessible"])

    def test_sync_creates_system_platforms_and_marks_them(self):
        self.client.force_authenticate(user=self.team_user)

        sync_res = self.client.post("/api/manage-platforms/sync/")
        self.assertEqual(sync_res.status_code, 200, sync_res.content)
        body = sync_res.json()

        self.assertGreaterEqual(body["stats"]["created"], 1)
        finance = ManagedPlatform.objects.get(slug="finance")
        self.assertEqual(finance.name, "Finance")

        list_res = self.client.get("/api/manage-platforms/")
        self.assertEqual(list_res.status_code, 200, list_res.content)
        rows = {row["slug"]: row for row in list_res.json()["results"]}
        self.assertTrue(rows["finance"]["is_system_defined"])

    def test_system_platform_cannot_be_deleted(self):
        ManagedPlatform.objects.create(name="Finance", slug="finance", status="ACTIVE", allow_non_team_users=True)
        self.client.force_authenticate(user=self.team_user)

        platform = ManagedPlatform.objects.get(slug="finance")
        delete_res = self.client.delete(f"/api/manage-platforms/{platform.id}/")

        self.assertEqual(delete_res.status_code, 403, delete_res.content)
        self.assertTrue(ManagedPlatform.objects.filter(slug="finance").exists())

    def test_audit_entries_are_written_for_create_update_delete(self):
        self.client.force_authenticate(user=self.team_user)

        create_res = self.client.post(
            "/api/manage-platforms/",
            {
                "name": "Music Sandbox",
                "slug": "music-sandbox",
                "status": "ACTIVE",
                "allow_non_team_users": True,
                "status_note": "",
            },
            format="json",
        )
        self.assertEqual(create_res.status_code, 201, create_res.content)
        platform_id = create_res.json()["id"]

        create_entry = ActivityEntry.objects.filter(event_type="managed_platform_created").order_by("-created_at").first()
        self.assertIsNotNone(create_entry)
        self.assertEqual(create_entry.metadata.get("platform_id"), platform_id)
        self.assertEqual(create_entry.actor_id, self.team_profile.id)

        update_res = self.client.patch(
            f"/api/manage-platforms/{platform_id}/",
            {
                "status": "LOCKED",
                "status_note": "Incident",
            },
            format="json",
        )
        self.assertEqual(update_res.status_code, 200, update_res.content)

        update_entry = ActivityEntry.objects.filter(event_type="managed_platform_updated").order_by("-created_at").first()
        self.assertIsNotNone(update_entry)
        self.assertEqual(update_entry.metadata.get("platform_id"), platform_id)
        self.assertEqual(update_entry.metadata.get("before", {}).get("status"), "ACTIVE")
        self.assertEqual(update_entry.metadata.get("status"), "LOCKED")

        delete_res = self.client.delete(f"/api/manage-platforms/{platform_id}/")
        self.assertEqual(delete_res.status_code, 204, delete_res.content)

        delete_entry = ActivityEntry.objects.filter(event_type="managed_platform_deleted").order_by("-created_at").first()
        self.assertIsNotNone(delete_entry)
        self.assertEqual(delete_entry.metadata.get("platform_id"), platform_id)

from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import ContentScheduleItem, Profile


class ContentScheduleApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="schedule-user", password="pw123456")
        self.profile = Profile.objects.create(user=self.user, name="Scheduler")

        self.other_user = User.objects.create_user(username="schedule-other", password="pw123456")
        self.other_profile = Profile.objects.create(user=self.other_user, name="Other")

        self.client.force_authenticate(user=self.user)

    def test_create_item_binds_to_authenticated_profile(self):
        payload = {
            "scheduled_date": "2026-05-25",
            "platform": "youtube",
            "status": "draft",
            "title": "Drop teaser",
            "note": "with hashtags",
            "sort_order": 0,
        }
        res = self.client.post("/api/content-schedule-items/", payload, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        item = ContentScheduleItem.objects.get(id=res.json()["id"])
        self.assertEqual(item.profile_id, self.profile.id)

    def test_list_filters_by_week_date_range(self):
        ContentScheduleItem.objects.create(
            profile=self.profile,
            scheduled_date=date(2026, 5, 26),
            platform="instagram",
            status="ready",
            title="Inside studio",
            sort_order=1,
        )
        ContentScheduleItem.objects.create(
            profile=self.profile,
            scheduled_date=date(2026, 6, 10),
            platform="blog",
            status="draft",
            title="Long form",
            sort_order=0,
        )
        res = self.client.get(
            "/api/content-schedule-items/",
            {"start_date": "2026-05-25", "end_date": "2026-05-31"},
        )
        self.assertEqual(res.status_code, 200, res.content)
        rows = res.json()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["scheduled_date"], "2026-05-26")

    def test_reorder_updates_sort_order(self):
        first = ContentScheduleItem.objects.create(
            profile=self.profile,
            scheduled_date=date(2026, 5, 25),
            platform="youtube",
            status="draft",
            title="One",
            sort_order=0,
        )
        second = ContentScheduleItem.objects.create(
            profile=self.profile,
            scheduled_date=date(2026, 5, 25),
            platform="tiktok",
            status="ready",
            title="Two",
            sort_order=1,
        )

        res = self.client.post(
            "/api/content-schedule-items/reorder/",
            {
                "items": [
                    {"id": first.id, "sort_order": 2},
                    {"id": second.id, "sort_order": 0},
                ]
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.content)

        first.refresh_from_db()
        second.refresh_from_db()
        self.assertEqual(first.sort_order, 2)
        self.assertEqual(second.sort_order, 0)

    def test_reorder_rejects_foreign_item(self):
        foreign = ContentScheduleItem.objects.create(
            profile=self.other_profile,
            scheduled_date=date(2026, 5, 25),
            platform="youtube",
            status="draft",
            title="Foreign",
            sort_order=0,
        )
        res = self.client.post(
            "/api/content-schedule-items/reorder/",
            {"items": [{"id": foreign.id, "sort_order": 1}]},
            format="json",
        )
        self.assertEqual(res.status_code, 404, res.content)

    def test_patch_can_move_item_to_another_day(self):
        item = ContentScheduleItem.objects.create(
            profile=self.profile,
            scheduled_date=date(2026, 5, 25),
            platform="youtube",
            status="draft",
            title="Move me",
            sort_order=0,
        )
        res = self.client.patch(
            f"/api/content-schedule-items/{item.id}/",
            {"scheduled_date": "2026-05-27", "sort_order": 1},
            format="json",
        )
        self.assertEqual(res.status_code, 200, res.content)
        item.refresh_from_db()
        self.assertEqual(str(item.scheduled_date), "2026-05-27")
        self.assertEqual(item.sort_order, 1)

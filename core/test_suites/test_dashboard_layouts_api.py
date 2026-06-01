from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Profile


class DashboardLayoutsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="layout-user", password="pw123456")
        self.profile = Profile.objects.create(user=self.user, name="Layout User")
        self.client.force_authenticate(user=self.user)

    def test_can_store_and_read_dashboard_layouts(self):
        payload = {
            "layouts": [
                {
                    "id": "layout-main",
                    "name": "Main",
                    "widgets": [
                        {"id": "priorities", "size": "m"},
                        {"id": "reviews", "size": "l"},
                    ],
                },
                {
                    "id": "layout-compact",
                    "name": "Compact",
                    "widgets": [{"id": "deadlines", "size": "s"}],
                },
            ],
            "active_layout_id": "layout-compact",
        }

        put_res = self.client.put("/api/dashboard/layouts/", payload, format="json")
        self.assertEqual(put_res.status_code, 200, put_res.content)
        self.assertEqual(put_res.json()["active_layout_id"], "layout-compact")
        self.assertEqual(len(put_res.json()["layouts"]), 2)

        get_res = self.client.get("/api/dashboard/layouts/")
        self.assertEqual(get_res.status_code, 200, get_res.content)
        self.assertEqual(get_res.json()["active_layout_id"], "layout-compact")
        self.assertEqual(len(get_res.json()["layouts"]), 2)

    def test_rejects_more_than_five_layouts(self):
        payload = {
            "layouts": [
                {"id": f"layout-{index}", "name": f"Layout {index}", "widgets": []}
                for index in range(6)
            ],
            "active_layout_id": "layout-0",
        }

        res = self.client.put("/api/dashboard/layouts/", payload, format="json")
        self.assertEqual(res.status_code, 400, res.content)

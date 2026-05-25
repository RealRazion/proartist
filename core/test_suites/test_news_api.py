from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Profile, Role


class NewsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        team_role, _ = Role.objects.get_or_create(key="TEAM")
        self.user = User.objects.create_user(username="news-team", password="pw123456")
        self.profile = Profile.objects.create(user=self.user, name="News Team")
        self.profile.roles.add(team_role)

        self.client.force_authenticate(user=self.user)

    def test_team_can_create_news_with_image(self):
        upload = SimpleUploadedFile("post.jpg", b"fake-image-bytes", content_type="image/jpeg")
        res = self.client.post(
            "/api/news/",
            {
                "title": "Update",
                "body": "Body",
                "is_published": True,
                "image": upload,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, 201, res.content)
        payload = res.json()
        self.assertIn("image", payload)
        self.assertTrue(bool(payload["image"]))

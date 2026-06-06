from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import NewsPost, Notification, Profile, Role


class NewsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        team_role, _ = Role.objects.get_or_create(key="TEAM")
        artist_role, _ = Role.objects.get_or_create(key="ARTIST")

        self.user = User.objects.create_user(username="news-team")
        self.profile = Profile.objects.create(user=self.user, name="News Team")
        self.profile.roles.add(team_role)

        self.artist_opt_in_user = User.objects.create_user(
            username="news-opt-in",
            email="opt-in@example.com",
        )
        self.artist_opt_in = Profile.objects.create(
            user=self.artist_opt_in_user,
            name="News Opt In",
            notification_settings={"news_updates": True},
        )
        self.artist_opt_in.roles.add(artist_role)

        self.artist_opt_out_user = User.objects.create_user(
            username="news-opt-out",
            email="opt-out@example.com",
        )
        self.artist_opt_out = Profile.objects.create(
            user=self.artist_opt_out_user,
            name="News Opt Out",
            notification_settings={"news_updates": False},
        )
        self.artist_opt_out.roles.add(artist_role)

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

    @patch("core.views.send_notification_email")
    def test_published_news_notifies_and_emails_opted_in_profiles(self, send_mail_mock):
        res = self.client.post(
            "/api/news/",
            {
                "title": "Release Notes",
                "body": "Neue Features sind online.",
                "is_published": True,
                "send_email": True,
            },
            format="multipart",
        )
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.json()["emails_sent"], 1)

        notifications = Notification.objects.filter(notification_type="news")
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications.first().recipient_id, self.artist_opt_in.id)

        send_mail_mock.assert_called_once()
        kwargs = send_mail_mock.call_args.kwargs
        self.assertEqual(kwargs.get("recipients"), ["opt-in@example.com"])

    @patch("core.views.send_notification_email")
    def test_publish_action_can_skip_email_dispatch(self, send_mail_mock):
        post = NewsPost.objects.create(
            author=self.profile,
            title="Draft",
            body="Draft body",
            is_published=False,
        )
        res = self.client.post(
            f"/api/news/{post.id}/publish/",
            {"publish": True, "send_email": False},
            format="multipart",
        )
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json()["emails_sent"], 0)
        self.assertEqual(Notification.objects.filter(notification_type="news").count(), 1)
        send_mail_mock.assert_not_called()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Profile, Role, Song, SongVersion


class MusicLibraryApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        artist_role, _ = Role.objects.get_or_create(key="ARTIST")
        self.user = User.objects.create_user(username="music-user", password="pw123456")
        self.profile = Profile.objects.create(user=self.user, name="Music User")
        self.profile.roles.add(artist_role)

        self.client.force_authenticate(user=self.user)

    def test_song_metadata_and_version_without_file(self):
        song_res = self.client.post(
            "/api/songs/",
            {
                "title": "Night Drive",
                "description": "Dark club vibe",
                "status": "ACTIVE",
                "genre": "Drill",
                "mood": "Dark",
                "bpm": 142,
                "key_signature": "Am",
                "tags": ["club", "single"],
            },
            format="json",
        )
        self.assertEqual(song_res.status_code, 201, song_res.content)

        song_id = song_res.json()["id"]
        version_res = self.client.post(
            "/api/song-versions/",
            {
                "song": song_id,
                "notes": "Arrangement update",
                "is_mix_ready": True,
            },
            format="json",
        )
        self.assertEqual(version_res.status_code, 201, version_res.content)
        self.assertEqual(version_res.json()["version_number"], 1)
        self.assertIsNone(version_res.json()["file"])

    def test_final_version_is_unique_per_song(self):
        song = Song.objects.create(profile=self.profile, title="Unique Final")
        first = SongVersion.objects.create(song=song, version_number=1, is_final=True)

        second_res = self.client.post(
            "/api/song-versions/",
            {
                "song": song.id,
                "notes": "Now final",
                "is_final": True,
            },
            format="json",
        )
        self.assertEqual(second_res.status_code, 201, second_res.content)

        first.refresh_from_db()
        self.assertFalse(first.is_final)
        self.assertTrue(SongVersion.objects.get(id=second_res.json()["id"]).is_final)

    def test_rejects_non_audio_upload(self):
        song = Song.objects.create(profile=self.profile, title="Upload Validation")
        js_file = SimpleUploadedFile("evil.js", b"import x from 'y'", content_type="application/javascript")

        res = self.client.post(
            "/api/song-versions/",
            {
                "song": song.id,
                "file": js_file,
                "notes": "should fail",
            },
            format="multipart",
        )

        self.assertEqual(res.status_code, 400, res.content)
        self.assertIn("file", res.json())

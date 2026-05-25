from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import (
    Profile,
    Role,
    Tournament,
    TournamentBattle,
    TournamentSubmission,
)


class TournamentVotingRulesTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

        self.team_role, _ = Role.objects.get_or_create(key="TEAM")
        self.artist_role, _ = Role.objects.get_or_create(key="ARTIST")

        self.creator_user = User.objects.create_user(username="team-voting", password="pw123456")
        self.creator_profile = Profile.objects.create(user=self.creator_user, name="Team Voting")
        self.creator_profile.roles.add(self.team_role)

        self.left_user = User.objects.create_user(username="left-artist", password="pw123456")
        self.left_profile = Profile.objects.create(user=self.left_user, name="Left Artist")
        self.left_profile.roles.add(self.artist_role)

        self.right_user = User.objects.create_user(username="right-artist", password="pw123456")
        self.right_profile = Profile.objects.create(user=self.right_user, name="Right Artist")
        self.right_profile.roles.add(self.artist_role)

    def _build_battle(self, **tournament_overrides):
        tournament = Tournament.objects.create(
            created_by=self.creator_profile,
            title="Voting Test",
            description="",
            status="BATTLES",
            has_application_phase=False,
            voting_mode=tournament_overrides.pop("voting_mode", "COMMUNITY"),
            allow_vote_change=tournament_overrides.pop("allow_vote_change", True),
            min_account_age_hours=tournament_overrides.pop("min_account_age_hours", 0),
            max_votes_per_ip_per_hour=tournament_overrides.pop("max_votes_per_ip_per_hour", 20),
            require_phone_vote_verification=tournament_overrides.pop("require_phone_vote_verification", False),
            **tournament_overrides,
        )
        left_submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.left_profile,
            round_number=1,
            title="Left",
            media_url="https://example.com/left",
        )
        right_submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.right_profile,
            round_number=1,
            title="Right",
            media_url="https://example.com/right",
        )
        battle = TournamentBattle.objects.create(
            tournament=tournament,
            round_number=1,
            left_submission=left_submission,
            right_submission=right_submission,
            status="LIVE",
        )
        return battle, left_submission, right_submission

    def test_blocks_new_accounts_when_min_age_is_set(self):
        battle, left_submission, _ = self._build_battle(min_account_age_hours=24)

        voter_user = User.objects.create_user(username="fresh-voter", password="pw123456")
        voter_user.date_joined = timezone.now() - timedelta(hours=2)
        voter_user.save(update_fields=["date_joined"])
        voter_profile = Profile.objects.create(user=voter_user, name="Fresh Voter")
        voter_profile.roles.add(self.artist_role)

        self.client.force_authenticate(user=voter_user)
        res = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": left_submission.id},
            format="json",
        )

        self.assertEqual(res.status_code, 403, res.content)

    def test_blocks_vote_change_when_disabled(self):
        battle, left_submission, right_submission = self._build_battle(allow_vote_change=False)

        voter_user = User.objects.create_user(username="single-voter", password="pw123456")
        voter_profile = Profile.objects.create(user=voter_user, name="Single Voter")
        voter_profile.roles.add(self.artist_role)

        self.client.force_authenticate(user=voter_user)
        first = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": left_submission.id},
            format="json",
        )
        second = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": right_submission.id},
            format="json",
        )

        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(second.status_code, 400, second.content)

    def test_blocks_non_team_votes_for_jury_only_mode(self):
        battle, left_submission, _ = self._build_battle(voting_mode="JURY_ONLY")

        voter_user = User.objects.create_user(username="fan-voter", password="pw123456")
        voter_profile = Profile.objects.create(user=voter_user, name="Fan Voter")
        voter_profile.roles.add(self.artist_role)

        self.client.force_authenticate(user=voter_user)
        res = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": left_submission.id},
            format="json",
        )

        self.assertEqual(res.status_code, 403, res.content)

    def test_ip_vote_limit_blocks_second_account(self):
        battle, left_submission, _ = self._build_battle(max_votes_per_ip_per_hour=1)

        voter_one = User.objects.create_user(username="ip-voter-1", password="pw123456")
        profile_one = Profile.objects.create(user=voter_one, name="IP Voter One")
        profile_one.roles.add(self.artist_role)

        voter_two = User.objects.create_user(username="ip-voter-2", password="pw123456")
        profile_two = Profile.objects.create(user=voter_two, name="IP Voter Two")
        profile_two.roles.add(self.artist_role)

        self.client.force_authenticate(user=voter_one)
        first = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": left_submission.id},
            format="json",
        )

        self.client.force_authenticate(user=voter_two)
        second = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": left_submission.id},
            format="json",
        )

        self.assertEqual(first.status_code, 201, first.content)
        self.assertEqual(second.status_code, 429, second.content)

    def test_flagged_votes_visible_to_team_and_can_be_moderated(self):
        battle, left_submission, _ = self._build_battle(require_phone_vote_verification=True)

        voter_user = User.objects.create_user(username="flag-voter", password="pw123456")
        voter_profile = Profile.objects.create(user=voter_user, name="Flag Voter")
        voter_profile.roles.add(self.artist_role)

        self.client.force_authenticate(user=voter_user)
        vote_res = self.client.post(
            "/api/tournament-votes/",
            {"battle": battle.id, "selected_submission": left_submission.id, "phone_number": ""},
            format="json",
        )
        self.assertEqual(vote_res.status_code, 201, vote_res.content)
        self.assertEqual(vote_res.json()["moderation_status"], "PENDING_REVIEW")

        self.client.force_authenticate(user=self.creator_user)
        flags_res = self.client.get(f"/api/tournament-votes/flags/?tournament={battle.tournament_id}")
        self.assertEqual(flags_res.status_code, 200, flags_res.content)
        self.assertEqual(len(flags_res.json()), 1)

        battle_before = self.client.get(f"/api/tournament-battles/?tournament={battle.tournament_id}")
        battle_before_payload = battle_before.json()
        battle_before_results = battle_before_payload.get("results", battle_before_payload)
        self.assertEqual(battle_before_results[0]["votes_left"], 0)

        moderate_res = self.client.post(
            f"/api/tournament-votes/{vote_res.json()['id']}/moderate/",
            {"decision": "APPROVED"},
            format="json",
        )
        self.assertEqual(moderate_res.status_code, 200, moderate_res.content)

        battle_after = self.client.get(f"/api/tournament-battles/?tournament={battle.tournament_id}")
        battle_after_payload = battle_after.json()
        battle_after_results = battle_after_payload.get("results", battle_after_payload)
        self.assertEqual(battle_after_results[0]["votes_left"], 1)

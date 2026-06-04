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
    TournamentVote,
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

    def test_team_can_close_battle_and_auto_advance(self):
        tournament = Tournament.objects.create(
            created_by=self.creator_profile,
            title="Bracket Auto Advance",
            description="",
            status="BATTLES",
            has_application_phase=False,
        )

        left_a = TournamentSubmission.objects.create(tournament=tournament, profile=self.left_profile, round_number=1, title="A")
        right_a = TournamentSubmission.objects.create(tournament=tournament, profile=self.right_profile, round_number=1, title="B")

        user_c = User.objects.create_user(username="artist-c", password="pw123456")
        profile_c = Profile.objects.create(user=user_c, name="Artist C")
        profile_c.roles.add(self.artist_role)
        user_d = User.objects.create_user(username="artist-d", password="pw123456")
        profile_d = Profile.objects.create(user=user_d, name="Artist D")
        profile_d.roles.add(self.artist_role)

        left_b = TournamentSubmission.objects.create(tournament=tournament, profile=profile_c, round_number=1, title="C")
        right_b = TournamentSubmission.objects.create(tournament=tournament, profile=profile_d, round_number=1, title="D")

        battle_one = TournamentBattle.objects.create(
            tournament=tournament,
            round_number=1,
            left_submission=left_a,
            right_submission=right_a,
            status="LIVE",
        )
        battle_two = TournamentBattle.objects.create(
            tournament=tournament,
            round_number=1,
            left_submission=left_b,
            right_submission=right_b,
            status="LIVE",
        )

        self.client.force_authenticate(user=self.creator_user)
        close_one = self.client.post(
            f"/api/tournament-battles/{battle_one.id}/close/",
            {"winner_submission": left_a.id},
            format="json",
        )
        self.assertEqual(close_one.status_code, 200, close_one.content)

        close_two = self.client.post(
            f"/api/tournament-battles/{battle_two.id}/close/",
            {"winner_submission": left_b.id},
            format="json",
        )
        self.assertEqual(close_two.status_code, 200, close_two.content)

        next_round_battles = TournamentBattle.objects.filter(tournament=tournament, round_number=2)
        self.assertEqual(next_round_battles.count(), 1)
        next_battle = next_round_battles.first()
        self.assertEqual(next_battle.left_submission_id, left_a.id)
        self.assertEqual(next_battle.right_submission_id, left_b.id)

    def test_leaderboard_endpoint_returns_ranked_rows(self):
        battle, left_submission, right_submission = self._build_battle()

        voter_user = User.objects.create_user(username="leader-voter", password="pw123456")
        voter_profile = Profile.objects.create(user=voter_user, name="Leader Voter")
        voter_profile.roles.add(self.artist_role)

        TournamentVote.objects.create(
            battle=battle,
            voter=voter_profile,
            selected_submission=left_submission,
            moderation_status="APPROVED",
        )

        battle.status = "CLOSED"
        battle.winner_submission = left_submission
        battle.closed_at = timezone.now()
        battle.ends_at = timezone.now()
        battle.save(update_fields=["status", "winner_submission", "closed_at", "ends_at"])

        self.client.force_authenticate(user=self.creator_user)
        res = self.client.get(f"/api/tournaments/{battle.tournament_id}/leaderboard/")
        self.assertEqual(res.status_code, 200, res.content)
        rows = res.json().get("rows", [])
        self.assertTrue(rows)
        self.assertEqual(rows[0]["profile_id"], self.left_profile.id)

    def test_ranked_overview_returns_tiers_and_my_rank(self):
        battle, left_submission, _ = self._build_battle()

        for _ in range(4):
            voter_user = User.objects.create_user(username=f"ranked-voter-{_}", password="pw123456")
            profile = Profile.objects.create(user=voter_user, name=f"Ranked Voter {_}")
            profile.roles.add(self.artist_role)
            TournamentVote.objects.create(
                battle=battle,
                voter=profile,
                selected_submission=left_submission,
                moderation_status="APPROVED",
            )

        battle.status = "CLOSED"
        battle.winner_submission = left_submission
        battle.closed_at = timezone.now()
        battle.ends_at = timezone.now()
        battle.save(update_fields=["status", "winner_submission", "closed_at", "ends_at"])

        self.client.force_authenticate(user=self.left_user)
        res = self.client.get("/api/tournaments/ranked-overview/")
        self.assertEqual(res.status_code, 200, res.content)

        payload = res.json()
        self.assertIn("rows", payload)
        self.assertIn("rank_distribution", payload)
        self.assertEqual(payload.get("my_profile_id"), self.left_profile.id)
        self.assertEqual(payload.get("my_rank"), 1)

        top_row = payload["rows"][0]
        self.assertEqual(top_row["profile_id"], self.left_profile.id)
        self.assertIn(top_row["tier"]["key"], {"BRONZE", "SILBER", "GOLD", "PLATIN", "RUBIN"})
        self.assertGreaterEqual(top_row["ranked_points"], 0)

    def test_team_can_moderate_submission_status(self):
        tournament = Tournament.objects.create(
            created_by=self.creator_profile,
            title="Submission Moderation",
            description="",
            status="SUBMISSION_OPEN",
            has_application_phase=False,
        )
        submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.left_profile,
            round_number=1,
            title="Needs review",
            media_url="https://example.com/review",
            status="PENDING",
        )

        self.client.force_authenticate(user=self.creator_user)
        res = self.client.post(
            f"/api/tournament-submissions/{submission.id}/decision/",
            {"decision": "APPROVED"},
            format="json",
        )

        self.assertEqual(res.status_code, 200, res.content)
        submission.refresh_from_db()
        self.assertEqual(submission.status, "APPROVED")

    def test_battle_creation_requires_approved_submissions(self):
        tournament = Tournament.objects.create(
            created_by=self.creator_profile,
            title="Battle Guard",
            description="",
            status="BATTLES",
            has_application_phase=False,
        )
        pending_submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.left_profile,
            round_number=1,
            title="Pending",
            media_url="https://example.com/pending",
            status="PENDING",
        )
        approved_submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.right_profile,
            round_number=1,
            title="Approved",
            media_url="https://example.com/approved",
            status="APPROVED",
        )

        self.client.force_authenticate(user=self.creator_user)
        res = self.client.post(
            "/api/tournament-battles/",
            {
                "tournament": tournament.id,
                "round_number": 1,
                "left_submission": pending_submission.id,
                "right_submission": approved_submission.id,
                "status": "LIVE",
            },
            format="json",
        )

        self.assertEqual(res.status_code, 403, res.content)
        self.assertEqual(TournamentBattle.objects.filter(tournament=tournament).count(), 0)

    def test_team_can_bulk_moderate_submissions_for_single_round(self):
        tournament = Tournament.objects.create(
            created_by=self.creator_profile,
            title="Bulk Moderation",
            description="",
            status="SUBMISSION_OPEN",
            has_application_phase=False,
        )
        round_one_a = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.left_profile,
            round_number=1,
            title="R1-A",
            status="PENDING",
        )
        round_one_b = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.right_profile,
            round_number=1,
            title="R1-B",
            status="PENDING",
        )
        round_two = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.right_profile,
            round_number=2,
            title="R2",
            status="PENDING",
        )

        self.client.force_authenticate(user=self.creator_user)
        res = self.client.post(
            f"/api/tournaments/{tournament.id}/submissions/bulk-decision/",
            {"decision": "APPROVED", "round_number": 1},
            format="json",
        )

        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.json().get("updated_count"), 2)

        round_one_a.refresh_from_db()
        round_one_b.refresh_from_db()
        round_two.refresh_from_db()
        self.assertEqual(round_one_a.status, "APPROVED")
        self.assertEqual(round_one_b.status, "APPROVED")
        self.assertEqual(round_two.status, "PENDING")

    def test_team_can_update_ranked_config(self):
        self.client.force_authenticate(user=self.creator_user)
        read_res = self.client.get("/api/tournaments/ranked-config/")
        self.assertEqual(read_res.status_code, 200, read_res.content)
        tiers = read_res.json().get("tiers", [])
        self.assertTrue(tiers)

        bronze = next((row for row in tiers if row.get("tier_key") == "BRONZE"), None)
        self.assertIsNotNone(bronze)

        patch_res = self.client.patch(
            "/api/tournaments/ranked-config/",
            {
                "season": {"duration_months": 3},
                "tiers": [
                    {
                        "tier_key": "BRONZE",
                        "loss_penalty": 11,
                        "max_losses_without_penalty": 2,
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(patch_res.status_code, 200, patch_res.content)
        updated_bronze = next((row for row in patch_res.json().get("tiers", []) if row.get("tier_key") == "BRONZE"), None)
        self.assertEqual(updated_bronze.get("loss_penalty"), 11)
        self.assertEqual(updated_bronze.get("max_losses_without_penalty"), 2)

    def test_timeline_endpoint_returns_live_and_upcoming(self):
        now = timezone.now()
        Tournament.objects.create(
            created_by=self.creator_profile,
            title="Live Cup",
            status="BATTLES",
            has_application_phase=False,
            starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(hours=2),
        )
        Tournament.objects.create(
            created_by=self.creator_profile,
            title="Upcoming Cup",
            status="APPLICATION_OPEN",
            has_application_phase=False,
            starts_at=now + timedelta(days=1),
            is_recurring=True,
            recurrence_type="WEEKLY",
            next_starts_at=now + timedelta(days=8),
        )

        self.client.force_authenticate(user=self.left_user)
        res = self.client.get("/api/tournaments/timeline/")
        self.assertEqual(res.status_code, 200, res.content)

        payload = res.json()
        self.assertGreaterEqual(len(payload.get("current", [])), 1)
        self.assertGreaterEqual(len(payload.get("upcoming", [])), 1)

    def test_no_loss_tournament_does_not_count_losses(self):
        tournament = Tournament.objects.create(
            created_by=self.creator_profile,
            title="No Loss Cup",
            status="BATTLES",
            has_application_phase=False,
            is_no_loss=True,
        )
        left_submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.left_profile,
            round_number=1,
            title="Left",
            status="APPROVED",
        )
        right_submission = TournamentSubmission.objects.create(
            tournament=tournament,
            profile=self.right_profile,
            round_number=1,
            title="Right",
            status="APPROVED",
        )
        battle = TournamentBattle.objects.create(
            tournament=tournament,
            round_number=1,
            left_submission=left_submission,
            right_submission=right_submission,
            status="CLOSED",
            winner_submission=right_submission,
            closed_at=timezone.now(),
            ends_at=timezone.now(),
        )
        self.assertIsNotNone(battle.id)

        self.client.force_authenticate(user=self.left_user)
        res = self.client.get("/api/tournaments/ranked-overview/")
        self.assertEqual(res.status_code, 200, res.content)
        rows = res.json().get("rows", [])
        left_row = next((row for row in rows if row.get("profile_id") == self.left_profile.id), None)
        self.assertIsNotNone(left_row)
        self.assertEqual(left_row.get("losses"), 0)

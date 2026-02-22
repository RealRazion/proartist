from datetime import date

from django.db import transaction

from .models import GrowProGoal, Profile, Project, Task

TASK_PRIORITY_SCORE = {
    "LOW": 1,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3,
}


def _team_profiles():
    return Profile.objects.filter(roles__key="TEAM").distinct()


def compute_team_scores(team_profiles=None):
    team_profiles = list(team_profiles) if team_profiles is not None else list(_team_profiles())
    scores = {profile.id: 0 for profile in team_profiles}
    if not scores:
        return scores

    tasks = (
        Task.objects.filter(is_archived=False)
        .exclude(status="DONE")
        .prefetch_related("assignees")
    )
    for task in tasks:
        points = TASK_PRIORITY_SCORE.get(task.priority, 1)
        for assignee in task.assignees.all():
            if assignee.id in scores:
                scores[assignee.id] += points

    projects = Project.objects.filter(is_archived=False).prefetch_related("participants", "owners")
    for project in projects:
        members = {p.id for p in project.participants.all()} | {p.id for p in project.owners.all()}
        for member_id in members:
            if member_id in scores:
                scores[member_id] += 2

    return scores


def pick_lowest_score_member(scores):
    if not scores:
        return None
    return min(scores.items(), key=lambda entry: (entry[1], entry[0]))[0]


def assign_task_for_review(task):
    team_profiles = list(_team_profiles())
    if not team_profiles:
        return None
    scores = compute_team_scores(team_profiles)
    target_id = pick_lowest_score_member(scores)
    if not target_id:
        return None
    if not task.assignees.filter(id=target_id).exists():
        task.assignees.add(target_id)
    return target_id


def rebalance_growpro_assignments():
    team_profiles = list(_team_profiles())
    if not team_profiles:
        return {"assigned": 0, "rebalanced": 0}

    team_ids = {profile.id for profile in team_profiles}
    scores = compute_team_scores(team_profiles)

    goals = list(
        GrowProGoal.objects.filter(status__in=["ACTIVE", "ON_HOLD"]).select_related("assigned_team")
    )
    for goal in goals:
        if goal.assigned_team_id in team_ids:
            scores[goal.assigned_team_id] += 1

    unassigned = [goal for goal in goals if goal.assigned_team_id not in team_ids]
    assigned_count = 0

    with transaction.atomic():
        for goal in sorted(unassigned, key=lambda g: (g.due_date or date.max, g.created_at)):
            target_id = pick_lowest_score_member(scores)
            if not target_id:
                break
            goal.assigned_team_id = target_id
            goal.save(update_fields=["assigned_team"])
            scores[target_id] += 1
            assigned_count += 1

        rebalanced = 0
        if len(team_profiles) > 1 and goals:
            max_moves = len(goals) * 2
            for _ in range(max_moves):
                high_id = max(scores, key=scores.get)
                low_id = min(scores, key=scores.get)
                if scores[high_id] - scores[low_id] <= 2:
                    break
                candidates = [goal for goal in goals if goal.assigned_team_id == high_id]
                if not candidates:
                    break
                candidates.sort(key=lambda g: (g.due_date or date.max, g.created_at), reverse=True)
                move_goal = candidates[0]
                move_goal.assigned_team_id = low_id
                move_goal.save(update_fields=["assigned_team"])
                scores[high_id] -= 1
                scores[low_id] += 1
                rebalanced += 1

    return {"assigned": assigned_count, "rebalanced": rebalanced}

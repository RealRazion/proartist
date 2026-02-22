from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

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


def build_team_points_breakdown(team_profiles=None):
    team_profiles = list(team_profiles) if team_profiles is not None else list(_team_profiles())
    members = {
        profile.id: {
            "profile": {
                "id": profile.id,
                "name": profile.name or profile.user.username,
                "username": profile.user.username,
            },
            "total": 0,
            "tasks": [],
            "projects": [],
            "growpro": [],
        }
        for profile in team_profiles
    }
    if not members:
        return []

    tasks = (
        Task.objects.filter(is_archived=False)
        .exclude(status="DONE")
        .prefetch_related("assignees")
    )
    for task in tasks:
        points = TASK_PRIORITY_SCORE.get(task.priority, 1)
        for assignee in task.assignees.all():
            if assignee.id not in members:
                continue
            entry = {
                "id": task.id,
                "title": task.title,
                "priority": task.priority,
                "points": points,
                "project_id": task.project_id,
            }
            members[assignee.id]["tasks"].append(entry)
            members[assignee.id]["total"] += points

    projects = Project.objects.filter(is_archived=False).prefetch_related("participants", "owners")
    for project in projects:
        participants = {p.id: p for p in project.participants.all()}
        owners = {p.id: p for p in project.owners.all()}
        for member_id in {**participants, **owners}:
            if member_id not in members:
                continue
            entry = {"id": project.id, "title": project.title, "points": 2}
            members[member_id]["projects"].append(entry)
            members[member_id]["total"] += 2

    goals = GrowProGoal.objects.filter(status__in=["ACTIVE", "ON_HOLD"]).select_related("assigned_team")
    for goal in goals:
        if goal.assigned_team_id not in members:
            continue
        entry = {
            "id": goal.id,
            "title": goal.title,
            "status": goal.status,
            "points": 1,
            "due_date": goal.due_date,
        }
        members[goal.assigned_team_id]["growpro"].append(entry)
        members[goal.assigned_team_id]["total"] += 1

    return sorted(members.values(), key=lambda item: (-item["total"], item["profile"]["name"]))


def build_team_points_daily(team_profiles=None, days=7):
    team_profiles = list(team_profiles) if team_profiles is not None else list(_team_profiles())
    today = timezone.now().date()
    start = today - timedelta(days=max(days, 1) - 1)
    days_list = [start + timedelta(days=offset) for offset in range((today - start).days + 1)]

    stats = {
        profile.id: {
            "daily": {day: {"plus": 0, "minus": 0} for day in days_list},
            "today_plus_details": [],
            "today_minus_details": [],
        }
        for profile in team_profiles
    }
    if not stats:
        return {}

    tasks_created = (
        Task.objects.filter(created_at__date__range=(start, today), is_archived=False)
        .prefetch_related("assignees")
    )
    for task in tasks_created:
        points = TASK_PRIORITY_SCORE.get(task.priority, 1)
        day = task.created_at.date()
        for assignee in task.assignees.all():
            if assignee.id not in stats:
                continue
            stats[assignee.id]["daily"][day]["plus"] += points
            if day == today:
                stats[assignee.id]["today_plus_details"].append(
                    {"title": task.title, "points": points, "type": "task_created"}
                )

    tasks_completed = (
        Task.objects.filter(completed_at__date__range=(start, today))
        .prefetch_related("assignees")
    )
    for task in tasks_completed:
        points = TASK_PRIORITY_SCORE.get(task.priority, 1)
        day = task.completed_at.date()
        for assignee in task.assignees.all():
            if assignee.id not in stats:
                continue
            stats[assignee.id]["daily"][day]["minus"] += points
            if day == today:
                stats[assignee.id]["today_minus_details"].append(
                    {"title": task.title, "points": points, "type": "task_completed"}
                )

    projects_created = Project.objects.filter(created_at__date__range=(start, today), is_archived=False).prefetch_related(
        "participants", "owners"
    )
    for project in projects_created:
        day = project.created_at.date()
        members = {p.id for p in project.participants.all()} | {p.id for p in project.owners.all()}
        for member_id in members:
            if member_id not in stats:
                continue
            stats[member_id]["daily"][day]["plus"] += 2
            if day == today:
                stats[member_id]["today_plus_details"].append(
                    {"title": project.title, "points": 2, "type": "project_created"}
                )

    goals_created = GrowProGoal.objects.filter(
        created_at__date__range=(start, today),
        assigned_team__isnull=False,
    ).select_related("assigned_team")
    for goal in goals_created:
        member_id = goal.assigned_team_id
        if member_id not in stats:
            continue
        day = goal.created_at.date()
        stats[member_id]["daily"][day]["plus"] += 1
        if day == today:
            stats[member_id]["today_plus_details"].append(
                {"title": goal.title, "points": 1, "type": "growpro_created"}
            )

    summary = {}
    for member_id, data in stats.items():
        total_plus = sum(entry["plus"] for entry in data["daily"].values())
        total_minus = sum(entry["minus"] for entry in data["daily"].values())
        days_count = len(data["daily"]) or 1
        today_stats = data["daily"].get(today, {"plus": 0, "minus": 0})
        summary[member_id] = {
            "today_plus": today_stats["plus"],
            "today_minus": today_stats["minus"],
            "today_net": today_stats["plus"] - today_stats["minus"],
            "avg_daily_plus": round(total_plus / days_count, 2),
            "avg_daily_minus": round(total_minus / days_count, 2),
            "avg_daily_net": round((total_plus - total_minus) / days_count, 2),
            "today_plus_details": data["today_plus_details"],
            "today_minus_details": data["today_minus_details"],
        }
    return summary

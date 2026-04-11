from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_team_profile(profile):
    return bool(profile and profile.roles.filter(key="TEAM").exists())


def can_view_project(profile, project):
    if not profile or not project:
        return False
    return (
        is_team_profile(profile)
        or project.owners.filter(id=profile.id).exists()
        or project.participants.filter(id=profile.id).exists()
    )


def can_manage_project(profile, project):
    if not profile or not project:
        return False
    return is_team_profile(profile) or project.owners.filter(id=profile.id).exists()


def can_manage_project_tasks(profile, project):
    if not profile:
        return False
    if is_team_profile(profile):
        return True
    if not project:
        return False
    if project.owners.filter(id=profile.id).exists():
        return True
    return (
        project.participants.filter(id=profile.id).exists()
        and project.participant_task_access == "EDIT"
    )


def can_comment_on_project_tasks(profile, project):
    if can_manage_project_tasks(profile, project):
        return True
    if not profile or not project:
        return False
    return (
        project.participants.filter(id=profile.id).exists()
        and project.participant_task_access in {"COMMENT", "EDIT"}
    )


class IsTeam(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated: return False
        p = getattr(u, "profile", None)
        if not p: return False
        return is_team_profile(p)

class IsTeamOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        p = getattr(u, "profile", None)
        if not p:
            return False
        return is_team_profile(p)

from rest_framework.permissions import SAFE_METHODS, BasePermission

class IsTeam(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated: return False
        p = getattr(u, "profile", None)
        if not p: return False
        return p.roles.filter(key="TEAM").exists()

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
        return p.roles.filter(key="TEAM").exists()

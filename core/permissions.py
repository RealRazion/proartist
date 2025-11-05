from rest_framework.permissions import BasePermission

class IsTeam(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated: return False
        p = getattr(u, "profile", None)
        if not p: return False
        return p.roles.filter(key="TEAM").exists()

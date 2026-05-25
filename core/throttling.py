from rest_framework.throttling import SimpleRateThrottle


class _BaseIpThrottle(SimpleRateThrottle):
    def _client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RegisterRateThrottle(_BaseIpThrottle):
    scope = "register"

    def get_cache_key(self, request, view):
        email = (request.data.get("email") or "").strip().lower() if hasattr(request, "data") else ""
        return self.cache_format % {
            "scope": self.scope,
            "ident": f"{self._client_ip(request)}:{email}",
        }


class VerifyRegistrationRateThrottle(_BaseIpThrottle):
    scope = "verify_registration"

    def get_cache_key(self, request, view):
        email = (request.data.get("email") or "").strip().lower() if hasattr(request, "data") else ""
        return self.cache_format % {
            "scope": self.scope,
            "ident": f"{self._client_ip(request)}:{email}",
        }


class SetPasswordRateThrottle(_BaseIpThrottle):
    scope = "set_password"

    def get_cache_key(self, request, view):
        return self.cache_format % {
            "scope": self.scope,
            "ident": self._client_ip(request),
        }


class InviteUserRateThrottle(_BaseIpThrottle):
    scope = "invite_user"

    def get_cache_key(self, request, view):
        if getattr(request, "user", None) and request.user.is_authenticated:
            ident = f"user:{request.user.pk}"
        else:
            ident = f"ip:{self._client_ip(request)}"
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }

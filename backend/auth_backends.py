from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Allows users to log in with either their username OR their email address (case-insensitive).
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if not username or not password:
            return None

        clean_ident = str(username).strip()
        user = (
            User.objects.filter(
                Q(username__iexact=clean_ident) | Q(email__iexact=clean_ident)
            )
            .order_by("-is_active", "id")
            .first()
        )

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None

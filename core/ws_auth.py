# core/ws_auth.py
from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware   # ✅ richtiger Import für Channels 4
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        try:
            query = parse_qs(scope.get("query_string", b"").decode())
            token = (query.get("token") or [None])[0]
            scope["user"] = AnonymousUser()
            if token:
                access = AccessToken(token)
                user = await sync_to_async(User.objects.get)(id=access["user_id"])
                scope["user"] = user
        except Exception as e:
            print("❌ JWTAuthMiddleware error:", e)
        return await super().__call__(scope, receive, send)

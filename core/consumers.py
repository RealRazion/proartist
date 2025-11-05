import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .serializers import ChatMessageSerializer
from .models import ChatMessage

@sync_to_async
def _save_msg(thread_id, sender_profile, text):
    m = ChatMessage.objects.create(
        thread_id=thread_id,
        sender=sender_profile,
        text=text,
        read=True,  # sender hat eigene Nachricht sofort gelesen
    )
    return ChatMessageSerializer(m).data

@sync_to_async
def _resolve_profile(user):
    return user.profile

@sync_to_async
def _mark_thread_read(thread_id, reader):
    qs = (ChatMessage.objects
          .filter(thread_id=thread_id, read=False)
          .exclude(sender=reader))
    ids = list(qs.values_list("id", flat=True))
    if ids:
        qs.update(read=True)
    return ids

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.thread_id = self.scope["url_route"]["kwargs"]["thread_id"]
        self.group = f"chat_{self.thread_id}"
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            await self.close(); return
        profile = await _resolve_profile(self.user)
        self.profile = profile
        self.profile_id = profile.id
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data or "{}")
        action = data.get("type", "message")
        profile = getattr(self, "profile", None)
        if profile is None:
            profile = await _resolve_profile(self.user)
            self.profile = profile

        if action == "typing":
            is_typing = bool(data.get("is_typing"))
            await self.channel_layer.group_send(
                self.group,
                {"type": "chat.typing", "profile": profile.id, "is_typing": is_typing}
            )
            return

        if action == "read":
            updated = await _mark_thread_read(self.thread_id, profile)
            if updated:
                await self.channel_layer.group_send(
                    self.group,
                    {"type": "chat.read", "profile": profile.id, "message_ids": updated}
                )
            return

        text = (data.get("text") or "").strip()
        if not text:
            return
        msg = await _save_msg(self.thread_id, profile, text)
        await self.channel_layer.group_send(self.group, {"type": "chat.message", "message": msg})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"event": "message", "message": event["message"]}))

    async def chat_typing(self, event):
        if event["profile"] == self.profile_id:
            return
        payload = {"event": "typing", "profile": event["profile"], "is_typing": event["is_typing"]}
        await self.send(text_data=json.dumps(payload))

    async def chat_read(self, event):
        payload = {"event": "read", "profile": event["profile"], "message_ids": event["message_ids"]}
        await self.send(text_data=json.dumps(payload))

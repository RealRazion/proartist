from rest_framework import serializers
from .models import (Profile, Role, Example, Request, ChatThread, ChatMessage,
                     Project, Task, Contract, Payment, Release, Event, Booking)

class RoleSerializer(serializers.ModelSerializer):
    class Meta: model=Role; fields=["id","key"]

class ExampleSerializer(serializers.ModelSerializer):
    class Meta: model=Example; fields=["id","title","link","file","created_at","profile"]

class ProfileSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True, write_only=True, source="roles")
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model=Profile
        fields=[
            "id",
            "user",
            "username",
            "email",
            "name",
            "iban",
            "socials",
            "genre",
            "city",
            "roles",
            "role_ids",
            "onboarding_uploaded_example",
            "created_at",
        ]

class RequestSerializer(serializers.ModelSerializer):
    class Meta: model=Request; fields="__all__"

class ChatMessageSerializer(serializers.ModelSerializer):
    # nach außen einheitlich "text" liefern (DB-Feld "text")
    text = serializers.CharField(read_only=True)
    sender_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = ["id", "thread", "sender", "sender_name", "text", "file", "file_url", "file_name", "file_size", "read", "created_at"]
        read_only_fields = ["sender", "created_at", "read", "text", "file_name", "file_size", "file_url"]

    def get_sender_name(self, obj):
        return getattr(obj.sender, "name", "") or obj.sender.user.username

    def get_file_url(self, obj):
        return obj.file.url if obj.file else None

    def get_file_name(self, obj):
        if not obj.file:
            return None
        return obj.file.name.split("/")[-1]

    def get_file_size(self, obj):
        if not obj.file:
            return None
        try:
            return obj.file.size
        except Exception:
            return None

class ChatThreadSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    participants = serializers.SerializerMethodField()

    class Meta:
        model = ChatThread
        fields = ["id", "participants", "created_at", "messages"]

    def get_participants(self, obj):
        return [
            {"id": obj.a_id, "name": getattr(obj.a, "name", "") or obj.a.user.username},
            {"id": obj.b_id, "name": getattr(obj.b, "name", "") or obj.b.user.username},
        ]
class ProjectSerializer(serializers.ModelSerializer):
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="participants"
    )
    participants = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "description",
            "status",
            "created_at",
            "participants",
            "participant_ids",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = ["id", "created_at", "participants", "is_archived", "archived_at"]

    def get_participants(self, obj):
        return [
            {"id": p.id, "name": getattr(p, "name", "") or p.user.username}
            for p in obj.participants.all()
        ]

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        project = super().create(validated_data)
        if participants:
            project.participants.set(participants)
        return project

    def update(self, instance, validated_data):
        participants = validated_data.pop("participants", None)
        project = super().update(instance, validated_data)
        if participants is not None:
            project.participants.set(participants)
        return project

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields="__all__"
        read_only_fields = ["is_archived", "archived_at"]

class ContractSerializer(serializers.ModelSerializer):
    class Meta: model=Contract; fields="__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta: model=Payment; fields="__all__"

class ReleaseSerializer(serializers.ModelSerializer):
    class Meta: model=Release; fields="__all__"

class EventSerializer(serializers.ModelSerializer):
    class Meta: model=Event; fields="__all__"

class BookingSerializer(serializers.ModelSerializer):
    class Meta: model=Booking; fields="__all__"

from rest_framework import serializers

from .models import (
    ActivityEntry,
    Booking,
    ChatMessage,
    ChatThread,
    Contract,
    Event,
    Example,
    NewsPost,
    Payment,
    Profile,
    Project,
    ProjectAttachment,
    Release,
    Request,
    Role,
    Task,
    TaskAttachment,
    TaskComment,
)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "key"]


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Example
        fields = ["id", "title", "link", "file", "created_at", "profile"]


class ProfileMiniSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "name", "username"]


class ProfileSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        many=True,
        write_only=True,
        source="roles",
    )
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    is_locked = serializers.SerializerMethodField()
    is_team_member = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
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
            "is_locked",
            "is_team_member",
            "onboarding_uploaded_example",
            "created_at",
        ]

    def update(self, instance, validated_data):
        roles = validated_data.get("roles")
        request = self.context.get("request")
        if roles is not None and request:
            requester_profile = getattr(request.user, "profile", None)
            if not requester_profile or not requester_profile.roles.filter(key="TEAM").exists():
                roles = [role for role in roles if role.key != "TEAM"]
                validated_data["roles"] = roles
        return super().update(instance, validated_data)

    def get_is_locked(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return False
        return not user.is_active

    def get_is_team_member(self, obj):
        return obj.roles.filter(key="TEAM").exists()


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = "__all__"


class ChatMessageSerializer(serializers.ModelSerializer):
    text = serializers.CharField(read_only=True)
    sender_name = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = [
            "id",
            "thread",
            "sender",
            "sender_name",
            "text",
            "file",
            "file_url",
            "file_name",
            "file_size",
            "read",
            "created_at",
        ]
        read_only_fields = [
            "sender",
            "created_at",
            "read",
            "text",
            "file_name",
            "file_size",
            "file_url",
        ]

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
        source="participants",
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
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_title",
            "title",
            "status",
            "priority",
            "assignee",
            "due_date",
            "created_at",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = ["is_archived", "archived_at", "created_at", "project_title"]


class ProjectAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    uploaded_by = ProfileMiniSerializer(read_only=True)

    class Meta:
        model = ProjectAttachment
        fields = ["id", "project", "label", "file", "file_url", "file_name", "uploaded_by", "created_at"]
        read_only_fields = ["uploaded_by", "created_at", "file_url", "file_name"]

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, "url"):
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if not obj.file:
            return None
        return obj.file.name.split("/")[-1]


class TaskAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    uploaded_by = ProfileMiniSerializer(read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ["id", "task", "label", "file", "file_url", "file_name", "uploaded_by", "created_at"]
        read_only_fields = ["uploaded_by", "created_at", "file_url", "file_name"]

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, "url"):
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if not obj.file:
            return None
        return obj.file.name.split("/")[-1]


class TaskCommentSerializer(serializers.ModelSerializer):
    author = ProfileMiniSerializer(read_only=True)
    mentions = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), many=True, required=False
    )
    mention_profiles = ProfileMiniSerializer(source="mentions", many=True, read_only=True)

    class Meta:
        model = TaskComment
        fields = ["id", "task", "author", "body", "mentions", "mention_profiles", "created_at"]
        read_only_fields = ["author", "created_at", "mention_profiles"]


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = "__all__"


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


class ActivityEntrySerializer(serializers.ModelSerializer):
    actor = ProfileMiniSerializer(read_only=True)
    project = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = ActivityEntry
        fields = [
            "id",
            "event_type",
            "title",
            "description",
            "severity",
            "actor",
            "project",
            "task",
            "metadata",
            "created_at",
        ]

    def get_project(self, obj):
        if not obj.project:
            return None
        return {"id": obj.project_id, "title": obj.project.title}

    def get_task(self, obj):
        if not obj.task:
            return None
        return {"id": obj.task_id, "title": obj.task.title}


class NewsPostSerializer(serializers.ModelSerializer):
    author = ProfileMiniSerializer(read_only=True)

    class Meta:
        model = NewsPost
        fields = ["id", "title", "body", "author", "is_published", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]

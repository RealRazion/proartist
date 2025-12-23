from rest_framework import serializers

from .models import (
    ActivityEntry,
    Booking,
    ChatMessage,
    ChatThread,
    Contract,
    Event,
    Example,
    Song,
    SongVersion,
    GrowProGoal,
    GrowProUpdate,
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
        required=False,
    )
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.SerializerMethodField()
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
            "notification_settings",
            "genre",
            "city",
            "roles",
            "role_ids",
            "is_locked",
            "is_team_member",
            "onboarding_uploaded_example",
            "created_at",
        ]
        read_only_fields = [
            "user",
            "username",
            "email",
            "roles",
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

    def get_email(self, obj):
        request = self.context.get("request")
        me = getattr(getattr(request, "user", None), "profile", None) if request else None
        if not me or not me.roles.filter(key="TEAM").exists():
            return None
        return getattr(obj.user, "email", "")


class RequestSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = "__all__"

    def get_sender_name(self, obj):
        return getattr(obj.sender, "name", "") or obj.sender.user.username

    def get_receiver_name(self, obj):
        return getattr(obj.receiver, "name", "") or obj.receiver.user.username


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
    owner_ids = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="owners",
    )
    owners = serializers.SerializerMethodField()

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
            "owners",
            "owner_ids",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = ["id", "created_at", "participants", "owners", "is_archived", "archived_at"]

    def get_participants(self, obj):
        return [
            {"id": p.id, "name": getattr(p, "name", "") or p.user.username}
            for p in obj.participants.all()
        ]

    def get_owners(self, obj):
        return [
            {"id": p.id, "name": getattr(p, "name", "") or p.user.username}
            for p in obj.owners.all()
        ]

    def create(self, validated_data):
        participants = validated_data.pop("participants", [])
        owners = validated_data.pop("owners", [])
        project = super().create(validated_data)
        if participants:
            project.participants.set(participants)
        if owners:
            project.owners.set(owners)
        return project

    def update(self, instance, validated_data):
        participants = validated_data.pop("participants", None)
        owners = validated_data.pop("owners", None)
        project = super().update(instance, validated_data)
        if participants is not None:
            project.participants.set(participants)
        if owners is not None:
            project.owners.set(owners)
        return project


class TaskSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    stakeholder_ids = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="stakeholders",
    )
    stakeholders = ProfileMiniSerializer(many=True, read_only=True)
    assignee_ids = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source="assignees",
    )
    assignees = ProfileMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "project",
            "project_title",
            "title",
            "status",
            "priority",
            "assignees",
            "assignee_ids",
            "due_date",
            "task_type",
            "stakeholders",
            "stakeholder_ids",
            "created_at",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = [
            "is_archived",
            "archived_at",
            "created_at",
            "project_title",
            "stakeholders",
            "assignees",
        ]
        extra_kwargs = {
            "project": {"allow_null": True, "required": False},
        }

    def create(self, validated_data):
        stakeholders = validated_data.pop("stakeholders", [])
        assignees = validated_data.pop("assignees", [])
        task = super().create(validated_data)
        if stakeholders:
            task.stakeholders.set(stakeholders)
        if assignees:
            task.assignees.set(assignees)
        return task

    def update(self, instance, validated_data):
        stakeholders = validated_data.pop("stakeholders", None)
        assignees = validated_data.pop("assignees", None)
        task = super().update(instance, validated_data)
        if stakeholders is not None:
            task.stakeholders.set(stakeholders)
        if assignees is not None:
            task.assignees.set(assignees)
        return task


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


class SongVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongVersion
        fields = "__all__"
        read_only_fields = ["created_at", "version_number"]

    def validate(self, attrs):
        # Datei nur bei Erstellung zwingend, bei PATCH kann sie fehlen
        if not self.instance and not attrs.get("file"):
            raise serializers.ValidationError({"file": "Datei ist erforderlich"})
        return attrs

    def create(self, validated_data):
        song = validated_data["song"]
        if "version_number" not in validated_data or not validated_data.get("version_number"):
            last = song.versions.order_by("-version_number").first()
            validated_data["version_number"] = (last.version_number + 1) if last else 1
        return super().create(validated_data)


class SongSerializer(serializers.ModelSerializer):
    profile = ProfileMiniSerializer(read_only=True)
    versions = SongVersionSerializer(many=True, read_only=True)
    project_title = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            "id",
            "profile",
            "project",
            "project_title",
            "title",
            "description",
            "status",
            "created_at",
            "versions",
        ]
        read_only_fields = ["id", "profile", "project_title", "created_at", "versions"]

    def get_project_title(self, obj):
        return obj.project.title if obj.project else None

    def validate(self, attrs):
        request = self.context.get("request")
        me = getattr(getattr(request, "user", None), "profile", None) if request else None
        if not me:
            return attrs
        is_team = me.roles.filter(key="TEAM").exists()
        if not is_team:
            if "project" in attrs:
                raise serializers.ValidationError({"project": "Nur Team darf Projekte zuweisen"})
        return attrs


class GrowProUpdateSerializer(serializers.ModelSerializer):
    created_by = ProfileMiniSerializer(read_only=True)

    class Meta:
        model = GrowProUpdate
        fields = ["id", "goal", "value", "note", "created_by", "created_at"]
        read_only_fields = ["id", "created_by", "created_at"]


class GrowProGoalSerializer(serializers.ModelSerializer):
    profile = ProfileMiniSerializer(read_only=True)
    created_by = ProfileMiniSerializer(read_only=True)
    updates = GrowProUpdateSerializer(many=True, read_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), source="profile", write_only=True, required=False
    )

    class Meta:
        model = GrowProGoal
        fields = [
            "id",
            "profile",
            "profile_id",
            "created_by",
            "title",
            "description",
            "metric",
            "unit",
            "target_value",
            "current_value",
            "due_date",
            "status",
            "last_logged_at",
            "created_at",
            "updated_at",
            "updates",
        ]
        read_only_fields = ["id", "created_by", "last_logged_at", "created_at", "updated_at", "updates"]

    def validate(self, attrs):
        request = self.context.get("request")
        me = getattr(getattr(request, "user", None), "profile", None) if request else None
        if not me:
            return attrs
        is_team = me.roles.filter(key="TEAM").exists()
        if not is_team:
            attrs["profile"] = me
        return attrs


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

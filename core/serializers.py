from calendar import monthrange
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone
from rest_framework import serializers
from django.db import transaction

from .models import (
    ActivityEntry,
    AutomationRule,
    Booking,
    ChatMessage,
    ChatThread,
    ContentScheduleItem,
    Contract,
    DailyExpense,
    Debt,
    DebtPayment,
    Event,
    Example,
    FinanceEntry,
    FinanceMember,
    FinanceProject,
    FinanceTip,
    GrowProGoal,
    GrowProUpdate,
    NewsPost,
    Notification,
    ManagedPlatform,
    Payment,
    Profile,
    PluginGuideImage,
    ProjectAttachment,
    PluginGuide,
    Project,
    Release,
    Request,
    RankedSeasonSettings,
    RankTierConfig,
    RegistrationRequest,
    Role,
    Song,
    SongVersion,
    SystemIntegration,
    Task,
    TaskAttachment,
    TaskComment,
    Tournament,
    TournamentApplication,
    TournamentBattle,
    TournamentSubmission,
    TournamentVote,
)
from .file_validators import validate_audio_file
from .platform_registry import is_system_platform


DECIMAL_2 = Decimal("0.01")


def _money(value):
    return Decimal(value or 0).quantize(DECIMAL_2, rounding=ROUND_HALF_UP)


def _resolve_reference_date(context):
    request = (context or {}).get("request")
    raw_month = ""
    if request:
        raw_month = (request.query_params.get("month") or "").strip()
    if raw_month:
        try:
            year, month_value = map(int, raw_month.split("-"))
            return date(year, month_value, 1)
        except (TypeError, ValueError):
            pass
    return timezone.now().date()


def _safe_date(year, month, day):
    return date(year, month, min(day, monthrange(year, month)[1]))


def _add_months(source_date, months=1):
    month_index = source_date.month - 1 + months
    year = source_date.year + month_index // 12
    month = month_index % 12 + 1
    return _safe_date(year, month, source_date.day)


def _monthly_amount(entry, today):
    amount = _money(entry.amount)
    if not getattr(entry, "is_active", True):
        return Decimal("0.00")

    month_end = _safe_date(today.year, today.month, monthrange(today.year, today.month)[1])
    if entry.frequency == "MONTHLY":
        if getattr(entry, "due_date", None) and entry.due_date > month_end:
            return Decimal("0.00")
        # Also check if due_day is set and the next due date is after month end
        if entry.due_day:
            next_due = _next_due_date(entry, today)
            if next_due and next_due > month_end:
                return Decimal("0.00")
        return amount
    if entry.frequency == "WEEKLY":
        if getattr(entry, "due_date", None) and entry.due_date > month_end:
            return Decimal("0.00")
        # Also check next due date for weekly entries
        next_due = _next_due_date(entry, today)
        if next_due and next_due > month_end:
            return Decimal("0.00")
        return (amount * Decimal("52") / Decimal("12")).quantize(DECIMAL_2, rounding=ROUND_HALF_UP)
    if entry.frequency == "YEARLY":
        if getattr(entry, "due_date", None):
            if entry.due_date.year > today.year or (
                entry.due_date.year == today.year and entry.due_date.month > today.month
            ):
                return Decimal("0.00")
        # Also check if due_day is set and the next due date is after current month
        if entry.due_day:
            next_due = _next_due_date(entry, today)
            if next_due and (next_due.year > today.year or (next_due.year == today.year and next_due.month > today.month)):
                return Decimal("0.00")
        return (amount / Decimal("12")).quantize(DECIMAL_2, rounding=ROUND_HALF_UP)
    if entry.frequency == "ONCE" and entry.due_date and entry.due_date.year == today.year and entry.due_date.month == today.month:
        return amount
    return Decimal("0.00")


def _next_due_date(entry, today):
    if not getattr(entry, "is_active", True):
        return None
    if entry.frequency == "ONCE":
        return entry.due_date if entry.due_date and entry.due_date >= today else None
    if entry.frequency == "MONTHLY":
        if getattr(entry, "due_date", None) and entry.due_date >= today:
            return entry.due_date
        if not entry.due_day:
            return None
        candidate = _safe_date(today.year, today.month, entry.due_day)
        if candidate < today:
            month_index = today.month
            year = today.year + month_index // 12
            month = month_index % 12 + 1
            candidate = _safe_date(year, month, entry.due_day)
        if getattr(entry, "due_date", None) and candidate < entry.due_date:
            return entry.due_date
        return candidate
    if entry.frequency == "WEEKLY":
        if not entry.due_date:
            return None
        if entry.due_date >= today:
            return entry.due_date
        weekday = entry.due_date.weekday()
        delta = (weekday - today.weekday()) % 7
        return today + timedelta(days=delta)
    if entry.frequency == "YEARLY":
        if not entry.due_date:
            return None
        if entry.due_date >= today:
            return entry.due_date
        candidate = _safe_date(today.year, entry.due_date.month, entry.due_date.day)
        if candidate < today:
            candidate = _safe_date(today.year + 1, entry.due_date.month, entry.due_date.day)
        return candidate
    return None


def _debt_monthly_amount(debt, today):
    if debt.status != "ACTIVE" or debt.is_fully_paid:
        return Decimal("0.00")

    month_end = _safe_date(today.year, today.month, monthrange(today.year, today.month)[1])

    # For installments, we budget one scheduled rate for the selected month as long as
    # the debt is active in that month. This prevents the monthly outflow from dropping
    # artificially after a due is marked as paid and next_due_date is moved forward.
    if debt.payment_type == "INSTALLMENT":
        if debt.start_date and debt.start_date > month_end:
            return Decimal("0.00")
        return _money(debt.scheduled_payment_amount)

    next_due = _debt_next_due_date(debt, today)
    if not next_due:
        return Decimal("0.00")
    if next_due > month_end:
        return Decimal("0.00")
    return _money(debt.scheduled_payment_amount)


def _default_debt_next_due_date(payment_type, start_date, due_day):
    if not start_date:
        return None
    if payment_type == "FIXED_AMOUNT":
        return start_date
    if not due_day:
        return None
    candidate = _safe_date(start_date.year, start_date.month, due_day)
    if candidate < start_date:
        candidate = _safe_date(
            start_date.year + (1 if start_date.month == 12 else 0),
            1 if start_date.month == 12 else start_date.month + 1,
            due_day,
        )
    return candidate


def _advance_debt_due_date(debt, current_due_date=None):
    if debt.payment_type != "INSTALLMENT" or not debt.due_day:
        return None
    base_due_date = current_due_date or _debt_next_due_date(debt, date.today())
    if not base_due_date:
        return None
    next_month_date = _add_months(base_due_date, 1)
    return _safe_date(next_month_date.year, next_month_date.month, debt.due_day)


def _debt_next_due_date(debt, today):
    if debt.status != "ACTIVE" or debt.is_fully_paid:
        return None
    stored_due_date = getattr(debt, "next_due_date", None)
    if stored_due_date:
        return stored_due_date
    if debt.payment_type == "FIXED_AMOUNT":
        return debt.start_date
    if not debt.due_day:
        return None
    reference_date = max(today, debt.start_date) if debt.start_date else today
    candidate = _safe_date(reference_date.year, reference_date.month, debt.due_day)
    if candidate < reference_date:
        candidate = _add_months(candidate, 1)
        candidate = _safe_date(candidate.year, candidate.month, debt.due_day)
    return candidate


def _debt_due_state(debt, today):
    if debt.is_fully_paid or debt.status == "PAID_OFF":
        return "PAID_OFF"
    if debt.status == "PAUSED":
        return "PAUSED"
    next_due = _debt_next_due_date(debt, today)
    if not next_due:
        return "SCHEDULED"
    if next_due < today:
        return "OVERDUE"
    if next_due == today:
        return "DUE_TODAY"
    return "UPCOMING"


def _to_float(value):
    return float(_money(value))


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


class RegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationRequest
        fields = ["id", "email", "description", "status", "invite_link", "created_at", "invited_at", "updated_at"]
        read_only_fields = ["invite_link", "created_at", "invited_at", "updated_at"]


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
            "color",
            "description",
            "status",
            "review_required",
            "created_at",
            "participants",
            "participant_ids",
            "owners",
            "owner_ids",
            "participant_task_access",
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
    created_by = ProfileMiniSerializer(read_only=True)
    updated_by = ProfileMiniSerializer(read_only=True)
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
            "review_required",
            "review_status",
            "priority",
            "assignees",
            "assignee_ids",
            "due_date",
            "task_type",
            "recurrence_pattern",
            "recurrence_interval",
            "recurrence_generated",
            "recurrence_parent",
            "stakeholders",
            "stakeholder_ids",
            "created_by",
            "updated_by",
            "created_at",
            "completed_at",
            "reviewed_at",
            "is_archived",
            "archived_at",
        ]
        read_only_fields = [
            "is_archived",
            "archived_at",
            "created_at",
            "completed_at",
            "reviewed_at",
            "project_title",
            "stakeholders",
            "assignees",
            "created_by",
            "updated_by",
            "recurrence_generated",
            "recurrence_parent",
        ]
        extra_kwargs = {
            "project": {"allow_null": True, "required": False},
        }

    def validate(self, attrs):
        recurrence_pattern = attrs.get("recurrence_pattern")
        if recurrence_pattern is None and self.instance is not None:
            recurrence_pattern = self.instance.recurrence_pattern
        recurrence_pattern = recurrence_pattern or "NONE"

        recurrence_interval = attrs.get("recurrence_interval")
        if recurrence_interval is None and self.instance is not None:
            recurrence_interval = self.instance.recurrence_interval
        recurrence_interval = recurrence_interval or 1

        due_date = attrs.get("due_date")
        if due_date is None and self.instance is not None:
            due_date = self.instance.due_date

        # Only validate recurrence when it's being explicitly set to non-NONE
        if "recurrence_pattern" in attrs and attrs["recurrence_pattern"] != "NONE" and not due_date:
            raise serializers.ValidationError({"due_date": "Wiederholende Tasks brauchen ein Fälligkeitsdatum."})
        if recurrence_interval and recurrence_interval < 1:
            raise serializers.ValidationError({"recurrence_interval": "Das Wiederholungsintervall muss mindestens 1 sein."})
        return attrs

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
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = SongVersion
        fields = [
            "id",
            "song",
            "version_number",
            "file",
            "file_url",
            "file_name",
            "notes",
            "duration_seconds",
            "is_mix_ready",
            "is_master_ready",
            "is_final",
            "created_at",
        ]
        read_only_fields = ["created_at", "version_number"]

    def validate(self, attrs):
        file = attrs.get("file")
        if file:
            try:
                validate_audio_file(file)
            except Exception as exc:
                raise serializers.ValidationError({"file": str(exc)})
        duration_seconds = attrs.get("duration_seconds")
        if duration_seconds is not None and duration_seconds > 60 * 60 * 4:
            raise serializers.ValidationError({"duration_seconds": "Dauer darf maximal 4 Stunden betragen."})
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            song = validated_data["song"]
            if "version_number" not in validated_data or not validated_data.get("version_number"):
                last = song.versions.order_by("-version_number").first()
                validated_data["version_number"] = (last.version_number + 1) if last else 1
            is_final = bool(validated_data.get("is_final"))
            if is_final:
                song.versions.filter(is_final=True).update(is_final=False)
            return super().create(validated_data)

    def update(self, instance, validated_data):
        with transaction.atomic():
            is_final = validated_data.get("is_final")
            if is_final is True:
                instance.song.versions.exclude(id=instance.id).filter(is_final=True).update(is_final=False)
            return super().update(instance, validated_data)

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, "url"):
            return obj.file.url
        return None

    def get_file_name(self, obj):
        if not obj.file:
            return None
        return obj.file.name.split("/")[-1]


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
            "genre",
            "mood",
            "bpm",
            "key_signature",
            "tags",
            "release_date",
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
        bpm = attrs.get("bpm")
        if bpm is not None and (bpm < 40 or bpm > 260):
            raise serializers.ValidationError({"bpm": "BPM muss zwischen 40 und 260 liegen."})
        tags = attrs.get("tags")
        if tags is not None:
            if not isinstance(tags, list):
                raise serializers.ValidationError({"tags": "Tags müssen als Liste gesendet werden."})
            cleaned = []
            for tag in tags:
                text = str(tag).strip()
                if text:
                    cleaned.append(text[:32])
            attrs["tags"] = cleaned[:12]
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
    assigned_team = ProfileMiniSerializer(read_only=True)
    updates = GrowProUpdateSerializer(many=True, read_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), source="profile", write_only=True, required=False
    )
    assigned_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(),
        source="assigned_team",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = GrowProGoal
        fields = [
            "id",
            "profile",
            "profile_id",
            "created_by",
            "assigned_team",
            "assigned_team_id",
            "title",
            "description",
            "metric",
            "unit",
            "target_value",
            "current_value",
            "due_date",
            "due_at",
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
            attrs.pop("assigned_team", None)
        assigned_team = attrs.get("assigned_team")
        if assigned_team and not assigned_team.roles.filter(key="TEAM").exists():
            raise serializers.ValidationError({"assigned_team_id": "Nur Team-Mitglieder können zugewiesen werden."})
        if self.instance is None and not attrs.get("metric"):
            title = (attrs.get("title") or "").strip()
            attrs["metric"] = title or "Ziel"
        return attrs


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class FinanceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinanceMember
        fields = ["id", "project", "name", "role", "notes", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


class FinanceEntrySerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    monthly_amount = serializers.SerializerMethodField()
    next_due_date = serializers.SerializerMethodField()

    class Meta:
        model = FinanceEntry
        fields = [
            "id",
            "project",
            "member",
            "member_name",
            "title",
            "category",
            "entry_type",
            "amount",
            "monthly_amount",
            "frequency",
            "due_day",
            "due_date",
            "next_due_date",
            "is_shared",
            "is_active",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "member_name", "monthly_amount", "next_due_date", "created_at", "updated_at"]

    def to_internal_value(self, data):
        cleaned = data.copy()
        for field in ("due_day", "due_date", "member"):
            if cleaned.get(field, serializers.empty) == "":
                cleaned[field] = None
        return super().to_internal_value(cleaned)

    def validate(self, attrs):
        frequency = attrs.get("frequency") or getattr(self.instance, "frequency", "MONTHLY")
        due_day = attrs.get("due_day", getattr(self.instance, "due_day", None))
        due_date = attrs.get("due_date", getattr(self.instance, "due_date", None))
        member = attrs.get("member", getattr(self.instance, "member", None))
        project = attrs.get("project", getattr(self.instance, "project", None))

        if frequency != "MONTHLY":
            attrs["due_day"] = None
            due_day = None

        if due_day is not None and (due_day < 1 or due_day > 31):
            raise serializers.ValidationError({"due_day": "Der Faelligkeitstag muss zwischen 1 und 31 liegen."})
        if frequency == "ONCE" and not due_date:
            raise serializers.ValidationError({"due_date": "Einmalige Posten brauchen ein Datum."})
        if member and project and member.project_id != project.id:
            raise serializers.ValidationError({"member": "Die Person gehoert nicht zu diesem Finanzprojekt."})
        return attrs

    def get_member_name(self, obj):
        return obj.member.name if obj.member else None

    def get_monthly_amount(self, obj):
        reference_date = _resolve_reference_date(self.context)
        return _to_float(_monthly_amount(obj, reference_date))

    def get_next_due_date(self, obj):
        reference_date = _resolve_reference_date(self.context)
        next_due = _next_due_date(obj, reference_date)
        return next_due.isoformat() if next_due else None


class DailyExpenseSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()

    class Meta:
        model = DailyExpense
        fields = [
            "id",
            "project",
            "member",
            "member_name",
            "date",
            "title",
            "category",
            "amount",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "member_name", "created_at", "updated_at"]

    def to_internal_value(self, data):
        cleaned = data.copy()
        if cleaned.get("member", serializers.empty) == "":
            cleaned["member"] = None
        return super().to_internal_value(cleaned)

    def validate(self, attrs):
        member = attrs.get("member", getattr(self.instance, "member", None))
        project = attrs.get("project", getattr(self.instance, "project", None))
        if member and project and member.project_id != project.id:
            raise serializers.ValidationError({"member": "Die Person gehoert nicht zu diesem Finanzprojekt."})
        return attrs

    def get_member_name(self, obj):
        return obj.member.name if obj.member else None


class FinanceProjectListSerializer(serializers.ModelSerializer):
    members = FinanceMemberSerializer(many=True, read_only=True)
    overview = serializers.SerializerMethodField()
    initial_members = serializers.ListField(
        child=serializers.CharField(max_length=120),
        write_only=True,
        required=False,
        allow_empty=True,
    )

    class Meta:
        model = FinanceProject
        fields = [
            "id",
            "title",
            "description",
            "currency",
            "current_balance",
            "dispo_limit",
            "dispo_used",
            "monthly_savings_target",
            "emergency_buffer_target",
            "savings_percentage",
            "members",
            "initial_members",
            "overview",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "members", "overview", "created_at", "updated_at"]

    def create(self, validated_data):
        initial_members = validated_data.pop("initial_members", [])
        project = super().create(validated_data)
        cleaned = []
        for raw_name in initial_members:
            name = (raw_name or "").strip()
            if name and name not in cleaned:
                cleaned.append(name)
        if not cleaned:
            owner = getattr(project.owner, "name", "") or getattr(project.owner.user, "username", "Ich")
            cleaned = [owner]
        FinanceMember.objects.bulk_create(
            [
                FinanceMember(
                    project=project,
                    name=name,
                    role="PRIMARY" if index == 0 else "PARTNER",
                    sort_order=index,
                )
                for index, name in enumerate(cleaned[:8])
            ]
        )
        return project

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = getattr(self, "instance", None)
        dispo_limit = _money(attrs.get("dispo_limit", getattr(instance, "dispo_limit", 0)))
        dispo_used = _money(attrs.get("dispo_used", getattr(instance, "dispo_used", 0)))
        if dispo_used < Decimal("0.00"):
            raise serializers.ValidationError({"dispo_used": "Dispo genutzt darf nicht negativ sein."})
        if dispo_used > dispo_limit:
            raise serializers.ValidationError({"dispo_used": "Dispo genutzt darf nicht groesser als Dispo verfuegbar sein."})
        return attrs

    def get_overview(self, obj):
        today = _resolve_reference_date(self.context)
        active_entries = list(obj.entries.filter(is_active=True).select_related("member"))
        debts = list(obj.debts.all())
        # Get daily expenses for selected month
        current_month_start = today.replace(day=1)
        next_month_start = _add_months(current_month_start, 1)
        daily_expenses = list(obj.daily_expenses.filter(date__gte=current_month_start, date__lt=next_month_start))

        totals = {
            "INCOME": Decimal("0.00"),
            "FIXED": Decimal("0.00"),
            "SUBSCRIPTION": Decimal("0.00"),
            "VARIABLE": Decimal("0.00"),
            "DEBT": Decimal("0.00"),
            "SAVING": Decimal("0.00"),
        }
        category_totals = {}
        member_totals = {}
        due_items = []
        month_entry_count = 0

        for member in obj.members.all():
            member_totals[member.id] = {
                "member_id": member.id,
                "member_name": member.name,
                "income": Decimal("0.00"),
                "outflow": Decimal("0.00"),
                "net": Decimal("0.00"),
            }
        shared_bucket = {
            "member_id": None,
            "member_name": "Gemeinsam",
            "income": Decimal("0.00"),
            "outflow": Decimal("0.00"),
            "net": Decimal("0.00"),
        }

        for entry in active_entries:
            monthly_amount = _monthly_amount(entry, today)
            if monthly_amount > 0:
                month_entry_count += 1
            totals[entry.entry_type] = totals.get(entry.entry_type, Decimal("0.00")) + monthly_amount
            if entry.category:
                category_totals[entry.category] = category_totals.get(entry.category, Decimal("0.00")) + monthly_amount

            bucket = shared_bucket if entry.is_shared or not entry.member_id else member_totals.get(entry.member_id)
            if bucket:
                if entry.entry_type == "INCOME":
                    bucket["income"] += monthly_amount
                    bucket["net"] += monthly_amount
                else:
                    bucket["outflow"] += monthly_amount
                    bucket["net"] -= monthly_amount

            next_due = _next_due_date(entry, today)
            if next_due and next_due <= today + timedelta(days=14):
                due_items.append(
                    {
                        "id": entry.id,
                        "title": entry.title,
                        "entry_type": entry.entry_type,
                        "amount": _to_float(entry.amount),
                        "monthly_amount": _to_float(monthly_amount),
                        "due_date": next_due.isoformat(),
                        "member_name": entry.member.name if entry.member else ("Gemeinsam" if entry.is_shared else None),
                        "frequency": entry.frequency,
                    }
                )

        total_remaining_debt = Decimal("0.00")
        total_remaining_credit = Decimal("0.00")
        monthly_credit_total = Decimal("0.00")
        month_debt_count = 0
        for debt in debts:
            if debt.status == "ACTIVE" and not debt.is_fully_paid:
                if debt.debt_kind == "CREDIT":
                    total_remaining_credit += debt.remaining_amount
                else:
                    total_remaining_debt += debt.remaining_amount
            monthly_amount = _debt_monthly_amount(debt, today)
            if monthly_amount > 0:
                month_debt_count += 1
                totals["DEBT"] += monthly_amount
                category_label = "Kredite" if debt.debt_kind == "CREDIT" else "Schulden"
                category_totals[category_label] = category_totals.get(category_label, Decimal("0.00")) + monthly_amount
                if debt.debt_kind == "CREDIT":
                    monthly_credit_total += monthly_amount
                shared_bucket["outflow"] += monthly_amount
                shared_bucket["net"] -= monthly_amount

            next_due = _debt_next_due_date(debt, today)
            if next_due and next_due <= today + timedelta(days=14):
                due_items.append(
                    {
                        "id": f"debt-{debt.id}",
                        "title": debt.name,
                        "entry_type": "DEBT",
                        "amount": _to_float(debt.scheduled_payment_amount),
                        "monthly_amount": _to_float(monthly_amount),
                        "due_date": next_due.isoformat(),
                        "member_name": "Kredite" if debt.debt_kind == "CREDIT" else "Schulden",
                        "frequency": debt.payment_type,
                    }
                )

        # Add daily expenses to totals and categories
        daily_expense_total = Decimal("0.00")
        for expense in daily_expenses:
            daily_expense_total += expense.amount
            if expense.category:
                category_totals[expense.category] = category_totals.get(expense.category, Decimal("0.00")) + expense.amount
            
            bucket = shared_bucket if not expense.member_id else member_totals.get(expense.member_id)
            if bucket:
                bucket["outflow"] += expense.amount
                bucket["net"] -= expense.amount

        month_daily_expense_count = len(daily_expenses)
        has_month_data = bool(month_entry_count or month_debt_count or month_daily_expense_count)
        monthly_outflow = (
            totals["FIXED"]
            + totals["SUBSCRIPTION"]
            + totals["VARIABLE"]
            + totals["DEBT"]
            + totals["SAVING"]
            + daily_expense_total
        )
        monthly_left = totals["INCOME"] - monthly_outflow
        projected_balance = _money(obj.current_balance) + monthly_left
        dispo_limit = _money(obj.dispo_limit)
        dispo_used = _money(getattr(obj, "dispo_used", 0))
        dispo_remaining = max(Decimal("0.00"), dispo_limit - dispo_used)
        projected_balance_with_dispo = projected_balance + dispo_remaining
        buffer_gap = max(Decimal("0.00"), _money(obj.emergency_buffer_target) - _money(obj.current_balance))

        member_rows = list(member_totals.values())
        if shared_bucket["income"] or shared_bucket["outflow"]:
            member_rows.append(shared_bucket)

        return {
            "snapshot_month": today.strftime("%Y-%m"),
            "people_count": obj.members.count(),
            "active_entry_count": len(active_entries),
            "month_entry_count": month_entry_count,
            "month_debt_count": month_debt_count,
            "month_daily_expense_count": month_daily_expense_count,
            "has_month_data": has_month_data,
            "monthly_income": _to_float(totals["INCOME"]),
            "monthly_fixed_costs": _to_float(totals["FIXED"]),
            "monthly_subscriptions": _to_float(totals["SUBSCRIPTION"]),
            "monthly_variable_costs": _to_float(totals["VARIABLE"]),
            "monthly_debt": _to_float(totals["DEBT"]),
            "monthly_credit": _to_float(monthly_credit_total),
            "monthly_savings": _to_float(totals["SAVING"]),
            "monthly_daily_expenses": _to_float(daily_expense_total),
            "monthly_outflow": _to_float(monthly_outflow),
            "monthly_left": _to_float(monthly_left),
            "total_remaining_debt": _to_float(total_remaining_debt),
            "total_debt": _to_float(total_remaining_debt),
            "total_remaining_credit": _to_float(total_remaining_credit),
            "total_credit": _to_float(total_remaining_credit),
            "current_balance": _to_float(obj.current_balance),
            "dispo_limit": _to_float(dispo_limit),
            "dispo_used": _to_float(dispo_used),
            "dispo_remaining": _to_float(dispo_remaining),
            "projected_balance": _to_float(projected_balance),
            "projected_balance_with_dispo": _to_float(projected_balance_with_dispo),
            "monthly_savings_target": _to_float(obj.monthly_savings_target),
            "emergency_buffer_target": _to_float(obj.emergency_buffer_target),
            "buffer_gap": _to_float(buffer_gap),
            "due_soon": sorted(due_items, key=lambda item: item["due_date"])[:6],
            "member_totals": [
                {
                    **row,
                    "income": _to_float(row["income"]),
                    "outflow": _to_float(row["outflow"]),
                    "net": _to_float(row["net"]),
                }
                for row in sorted(member_rows, key=lambda row: (row["member_id"] is None, row["member_name"]))
            ],
            "top_categories": [
                {"category": category, "amount": _to_float(amount)}
                for category, amount in sorted(category_totals.items(), key=lambda item: item[1], reverse=True)[:5]
            ],
        }


class FinanceProjectSerializer(FinanceProjectListSerializer):
    entries = FinanceEntrySerializer(many=True, read_only=True)

    class Meta(FinanceProjectListSerializer.Meta):
        fields = FinanceProjectListSerializer.Meta.fields[:-2] + ["entries", "created_at", "updated_at"]
        read_only_fields = FinanceProjectListSerializer.Meta.read_only_fields + ["entries"]


class DebtPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DebtPayment
        fields = ["id", "debt", "amount", "payment_date", "notes", "created_at"]
        read_only_fields = ["id", "created_at"]


class DebtPaymentActionSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=[("paid", "paid"), ("missed", "missed")])
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    date = serializers.DateField(required=False, allow_null=True)
    reschedule_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = data.copy()
            for field in ("date", "reschedule_date"):
                value = data.get(field)
                if value == "":
                    data[field] = None
                    continue
                if isinstance(value, str):
                    normalized = value.strip()
                    if not normalized:
                        data[field] = None
                        continue
                    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y/%m/%d"):
                        try:
                            data[field] = datetime.strptime(normalized, fmt).date().isoformat()
                            break
                        except ValueError:
                            continue
        return super().to_internal_value(data)

class DebtSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()
    debt_kind = serializers.ChoiceField(choices=Debt.DEBT_KINDS, required=False)
    payment_type = serializers.ChoiceField(choices=Debt.PAYMENT_TYPES, required=False)
    monthly_payment = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    due_day = serializers.IntegerField(required=False, allow_null=True)
    next_due_date = serializers.DateField(required=False, allow_null=True)
    paid_off_date = serializers.DateField(required=False, allow_null=True)
    remaining_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_fully_paid = serializers.BooleanField(read_only=True)
    months_remaining = serializers.IntegerField(read_only=True)
    payment_percentage = serializers.SerializerMethodField()
    scheduled_payment_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    due_state = serializers.SerializerMethodField()

    class Meta:
        model = Debt
        fields = [
            "id",
            "project",
            "name",
            "debt_kind",
            "payment_type",
            "total_amount",
            "amount_paid",
            "monthly_payment",
            "due_day",
            "next_due_date",
            "status",
            "start_date",
            "paid_off_date",
            "remaining_amount",
            "is_fully_paid",
            "months_remaining",
            "payment_percentage",
            "scheduled_payment_amount",
            "due_state",
            "payments",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "remaining_amount",
            "is_fully_paid",
            "months_remaining",
            "payment_percentage",
            "scheduled_payment_amount",
            "payments",
            "created_at",
            "updated_at",
        ]

    def get_payment_percentage(self, obj):
        total = float(obj.total_amount or 0)
        if total <= 0:
            return 0
        paid = float(obj.amount_paid or 0)
        return round((paid / total) * 100, 2)

    def get_due_state(self, obj):
        return _debt_due_state(obj, timezone.now().date())

    def get_payments(self, obj):
        return DebtPaymentSerializer(obj.payments.all(), many=True).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        next_due = _debt_next_due_date(instance, timezone.now().date())
        data["next_due_date"] = next_due.isoformat() if next_due else None
        return data

    def to_internal_value(self, data):
        cleaned = data.copy()
        for field in ("monthly_payment", "due_day", "next_due_date", "paid_off_date"):
            if cleaned.get(field, serializers.empty) == "":
                cleaned[field] = None
        return super().to_internal_value(cleaned)

    def validate(self, attrs):
        instance = self.instance
        payment_type = attrs.get("payment_type", getattr(instance, "payment_type", "INSTALLMENT"))
        total_amount = attrs.get("total_amount", getattr(instance, "total_amount", None))
        amount_paid = attrs.get("amount_paid", getattr(instance, "amount_paid", Decimal("0")))
        monthly_payment = attrs.get("monthly_payment", getattr(instance, "monthly_payment", None))
        due_day = attrs.get("due_day", getattr(instance, "due_day", None))
        start_date = attrs.get("start_date", getattr(instance, "start_date", None))
        next_due_date = attrs.get("next_due_date", getattr(instance, "next_due_date", None))
        status = attrs.get("status", getattr(instance, "status", "ACTIVE"))
        paid_off_date = attrs.get("paid_off_date", getattr(instance, "paid_off_date", None))
        explicit_next_due_date = "next_due_date" in attrs
        scheduling_changed = instance is None or any(field in attrs for field in ("payment_type", "start_date", "due_day"))

        errors = {}

        if total_amount is None or total_amount <= 0:
            errors["total_amount"] = "Der Gesamtbetrag muss groesser als 0 sein."

        if amount_paid is None or amount_paid < 0:
            errors["amount_paid"] = "Der bezahlte Betrag darf nicht negativ sein."
        elif total_amount is not None and amount_paid > total_amount:
            errors["amount_paid"] = "Der bezahlte Betrag darf die Gesamtschuld nicht uebersteigen."

        if due_day is not None and (due_day < 1 or due_day > 31):
            errors["due_day"] = "Der Faelligkeitstag muss zwischen 1 und 31 liegen."

        if payment_type == "INSTALLMENT":
            if monthly_payment is None:
                errors["monthly_payment"] = "Raten-Schulden brauchen eine monatliche Rate."
            elif monthly_payment <= 0:
                errors["monthly_payment"] = "Die monatliche Rate muss groesser als 0 sein."
            if due_day is None:
                errors["due_day"] = "Raten-Schulden brauchen einen Faelligkeitstag."
        else:
            attrs["monthly_payment"] = None
            attrs["due_day"] = None
            due_day = None
            monthly_payment = None

        if start_date is None:
            errors["start_date"] = "Ein Startdatum ist erforderlich."

        if next_due_date is not None and start_date is not None and next_due_date < start_date:
            errors["next_due_date"] = "Die naechste Faelligkeit darf nicht vor dem Startdatum liegen."

        if errors:
            raise serializers.ValidationError(errors)

        fully_paid = total_amount is not None and amount_paid >= total_amount
        if fully_paid:
            attrs["status"] = "PAID_OFF"
            attrs["paid_off_date"] = paid_off_date or date.today()
            attrs["next_due_date"] = None
        else:
            if status == "PAID_OFF":
                raise serializers.ValidationError(
                    {"status": "Der Status kann nur auf 'PAID_OFF' stehen, wenn die Schuld komplett bezahlt ist."}
                )
            attrs["paid_off_date"] = None
            if status == "ACTIVE" and ((scheduling_changed and not explicit_next_due_date) or next_due_date is None):
                if instance is not None and next_due_date is None and not scheduling_changed:
                    attrs["next_due_date"] = _debt_next_due_date(instance, timezone.now().date())
                else:
                    attrs["next_due_date"] = _default_debt_next_due_date(payment_type, start_date, due_day)
            elif status != "ACTIVE" and explicit_next_due_date and attrs.get("next_due_date") is None:
                attrs["next_due_date"] = _default_debt_next_due_date(payment_type, start_date, due_day)

        return attrs


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


class TournamentSerializer(serializers.ModelSerializer):
    created_by = ProfileMiniSerializer(read_only=True)
    applications_count = serializers.IntegerField(read_only=True)
    submissions_count = serializers.IntegerField(read_only=True)
    battles_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tournament
        fields = [
            "id",
            "created_by",
            "title",
            "description",
            "has_application_phase",
            "application_deadline",
            "submission_deadline",
            "status",
            "voting_mode",
            "allow_vote_change",
            "min_account_age_hours",
            "max_votes_per_ip_per_hour",
            "require_phone_vote_verification",
            "is_no_loss",
            "starts_at",
            "ends_at",
            "is_recurring",
            "recurrence_type",
            "recurrence_interval",
            "next_starts_at",
            "applications_count",
            "submissions_count",
            "battles_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_min_account_age_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("min_account_age_hours darf nicht negativ sein.")
        if value > 24 * 30:
            raise serializers.ValidationError("min_account_age_hours darf maximal 720 Stunden sein.")
        return value

    def validate_max_votes_per_ip_per_hour(self, value):
        if value < 1:
            raise serializers.ValidationError("max_votes_per_ip_per_hour muss mindestens 1 sein.")
        if value > 1000:
            raise serializers.ValidationError("max_votes_per_ip_per_hour darf maximal 1000 sein.")
        return value

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if starts_at and ends_at and starts_at >= ends_at:
            raise serializers.ValidationError({"ends_at": "ends_at muss nach starts_at liegen."})

        is_recurring = attrs.get("is_recurring", getattr(self.instance, "is_recurring", False))
        recurrence_type = attrs.get("recurrence_type", getattr(self.instance, "recurrence_type", "NONE"))
        recurrence_interval = attrs.get("recurrence_interval", getattr(self.instance, "recurrence_interval", 1))
        if is_recurring and recurrence_type == "NONE":
            raise serializers.ValidationError({"recurrence_type": "Bitte einen Wiederholungs-Typ waehlen."})
        if recurrence_interval < 1:
            raise serializers.ValidationError({"recurrence_interval": "recurrence_interval muss mindestens 1 sein."})
        if not is_recurring:
            attrs["recurrence_type"] = "NONE"
            attrs["recurrence_interval"] = 1
            attrs["next_starts_at"] = None

        return attrs


class RankedSeasonSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankedSeasonSettings
        fields = ["id", "duration_months", "seasons_per_year", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_duration_months(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("duration_months muss zwischen 1 und 12 liegen.")
        if 12 % value != 0:
            raise serializers.ValidationError("duration_months muss 12 ohne Rest teilen (z. B. 1, 2, 3, 4, 6, 12).")
        return value


class RankTierConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankTierConfig
        fields = [
            "id",
            "tier_key",
            "display_name",
            "accent",
            "min_points",
            "max_points",
            "win_points",
            "vote_points",
            "submission_points",
            "battle_points",
            "loss_penalty",
            "max_losses_without_penalty",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        min_points = attrs.get("min_points", getattr(self.instance, "min_points", 0))
        max_points = attrs.get("max_points", getattr(self.instance, "max_points", None))
        if max_points is not None and max_points < min_points:
            raise serializers.ValidationError({"max_points": "max_points muss groesser oder gleich min_points sein."})
        return attrs


class TournamentApplicationSerializer(serializers.ModelSerializer):
    profile = ProfileMiniSerializer(read_only=True)
    decided_by = ProfileMiniSerializer(read_only=True)
    tournament_title = serializers.CharField(source="tournament.title", read_only=True)

    class Meta:
        model = TournamentApplication
        fields = [
            "id",
            "tournament",
            "tournament_title",
            "profile",
            "message",
            "status",
            "decided_by",
            "decided_at",
            "created_at",
        ]
        read_only_fields = ["id", "profile", "status", "decided_by", "decided_at", "created_at", "tournament_title"]


class TournamentSubmissionSerializer(serializers.ModelSerializer):
    profile = ProfileMiniSerializer(read_only=True)
    tournament_title = serializers.CharField(source="tournament.title", read_only=True)

    class Meta:
        model = TournamentSubmission
        fields = [
            "id",
            "tournament",
            "tournament_title",
            "profile",
            "round_number",
            "title",
            "media_url",
            "notes",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "profile", "status", "created_at", "tournament_title"]


class TournamentBattleSerializer(serializers.ModelSerializer):
    left_submission_title = serializers.CharField(source="left_submission.title", read_only=True)
    right_submission_title = serializers.CharField(source="right_submission.title", read_only=True)
    left_profile_name = serializers.SerializerMethodField()
    right_profile_name = serializers.SerializerMethodField()
    votes_left = serializers.SerializerMethodField()
    votes_right = serializers.SerializerMethodField()
    winner_profile_name = serializers.SerializerMethodField()

    class Meta:
        model = TournamentBattle
        fields = [
            "id",
            "tournament",
            "round_number",
            "left_submission",
            "right_submission",
            "winner_submission",
            "left_submission_title",
            "right_submission_title",
            "left_profile_name",
            "right_profile_name",
            "winner_profile_name",
            "votes_left",
            "votes_right",
            "starts_at",
            "ends_at",
            "closed_at",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "winner_submission",
            "winner_profile_name",
            "votes_left",
            "votes_right",
            "closed_at",
            "created_at",
            "left_profile_name",
            "right_profile_name",
            "left_submission_title",
            "right_submission_title",
        ]

    def get_left_profile_name(self, obj):
        profile = getattr(getattr(obj.left_submission, "profile", None), "name", "")
        username = getattr(getattr(getattr(obj.left_submission, "profile", None), "user", None), "username", "")
        return profile or username

    def get_right_profile_name(self, obj):
        profile = getattr(getattr(obj.right_submission, "profile", None), "name", "")
        username = getattr(getattr(getattr(obj.right_submission, "profile", None), "user", None), "username", "")
        return profile or username

    def get_votes_left(self, obj):
        return obj.votes.filter(selected_submission=obj.left_submission, moderation_status="APPROVED").count()

    def get_votes_right(self, obj):
        return obj.votes.filter(selected_submission=obj.right_submission, moderation_status="APPROVED").count()

    def get_winner_profile_name(self, obj):
        if not obj.winner_submission:
            return ""
        profile = getattr(getattr(obj.winner_submission, "profile", None), "name", "")
        username = getattr(getattr(getattr(obj.winner_submission, "profile", None), "user", None), "username", "")
        return profile or username


class TournamentVoteSerializer(serializers.ModelSerializer):
    voter = ProfileMiniSerializer(read_only=True)
    voter_name = serializers.SerializerMethodField()
    tournament = serializers.IntegerField(source="battle.tournament_id", read_only=True)
    battle_round = serializers.IntegerField(source="battle.round_number", read_only=True)

    class Meta:
        model = TournamentVote
        fields = [
            "id",
            "tournament",
            "battle",
            "battle_round",
            "voter",
            "voter_name",
            "selected_submission",
            "phone_number",
            "is_flagged",
            "flag_reason",
            "moderation_status",
            "moderated_by",
            "moderated_at",
            "verification_status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "tournament",
            "battle_round",
            "voter",
            "voter_name",
            "is_flagged",
            "flag_reason",
            "moderation_status",
            "moderated_by",
            "moderated_at",
            "verification_status",
            "created_at",
        ]

    def get_voter_name(self, obj):
        profile_name = getattr(obj.voter, "name", "")
        username = getattr(getattr(obj.voter, "user", None), "username", "")
        return profile_name or username


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


class NotificationSerializer(serializers.ModelSerializer):
    actor = ProfileMiniSerializer(read_only=True)
    project = serializers.SerializerMethodField()
    task = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "body",
            "severity",
            "actor",
            "project",
            "task",
            "metadata",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "notification_type",
            "title",
            "body",
            "severity",
            "actor",
            "project",
            "task",
            "metadata",
            "read_at",
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
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = NewsPost
        fields = ["id", "title", "body", "author", "image", "image_url", "is_published", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request") if hasattr(self, "context") else None
        url = obj.image.url
        if request and hasattr(request, "build_absolute_uri"):
            return request.build_absolute_uri(url)
        return url


class FinanceTipSerializer(serializers.ModelSerializer):
    author = ProfileMiniSerializer(read_only=True)

    class Meta:
        model = FinanceTip
        fields = ["id", "title", "body", "tip_type", "author", "is_published", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]


class PluginGuideSerializer(serializers.ModelSerializer):
    author = ProfileMiniSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = PluginGuide
        fields = [
            "id",
            "title",
            "body",
            "author",
            "image",
            "image_url",
            "images",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["author", "created_at", "updated_at", "image_url", "images"]

    def get_image_url(self, obj):
        if not obj.image:
            return None
        return obj.image.url

    def get_images(self, obj):
        request = self.context.get("request") if hasattr(self, "context") else None
        rows = []
        for image in obj.images.all():
            url = image.image.url if image.image else None
            if url and request and hasattr(request, "build_absolute_uri"):
                url = request.build_absolute_uri(url)
            rows.append(
                {
                    "id": image.id,
                    "image_url": url,
                    "sort_order": image.sort_order,
                }
            )
        return rows


class AutomationRuleSerializer(serializers.ModelSerializer):
    created_by = ProfileMiniSerializer(read_only=True)

    class Meta:
        model = AutomationRule
        fields = [
            "id",
            "name",
            "trigger",
            "action",
            "config",
            "is_active",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_config(self, value):
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("Config muss ein Objekt sein.")
        return value


class SystemIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemIntegration
        fields = [
            "id",
            "name",
            "slug",
            "api_key",
            "scopes",
            "is_active",
            "last_used_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_used_at", "created_at", "updated_at"]


class ManagedPlatformSerializer(serializers.ModelSerializer):
    can_access_as_team = serializers.SerializerMethodField()
    can_access_as_non_team = serializers.SerializerMethodField()
    is_system_defined = serializers.SerializerMethodField()

    class Meta:
        model = ManagedPlatform
        fields = [
            "id",
            "name",
            "slug",
            "version",
            "status",
            "allow_non_team_users",
            "status_note",
            "updated_by",
            "can_access_as_team",
            "can_access_as_non_team",
            "is_system_defined",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "version", "updated_by", "can_access_as_team", "can_access_as_non_team", "is_system_defined", "created_at", "updated_at"]

    def get_can_access_as_team(self, obj):
        return obj.status != "LOCKED"

    def get_can_access_as_non_team(self, obj):
        if obj.status != "ACTIVE":
            return False
        return obj.allow_non_team_users

    def get_is_system_defined(self, obj):
        return is_system_platform(obj.slug)


class ContentScheduleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentScheduleItem
        fields = [
            "id",
            "profile",
            "scheduled_date",
            "platform",
            "status",
            "title",
            "note",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["profile", "created_at", "updated_at"]

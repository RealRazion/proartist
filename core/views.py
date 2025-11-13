import csv
import io
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count, Max, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ROLE_CHOICES,
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
from .permissions import IsTeam, IsTeamOrReadOnly
from .serializers import (
    ActivityEntrySerializer,
    BookingSerializer,
    ChatMessageSerializer,
    ChatThreadSerializer,
    ContractSerializer,
    EventSerializer,
    ExampleSerializer,
    NewsPostSerializer,
    PaymentSerializer,
    ProfileSerializer,
    ProjectAttachmentSerializer,
    ProjectSerializer,
    ReleaseSerializer,
    RequestSerializer,
    RoleSerializer,
    TaskAttachmentSerializer,
    TaskCommentSerializer,
    TaskSerializer,
)
from .utils import log_activity

# --- Auth/Register ---
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get("username"); email = request.data.get("email")
    password = request.data.get("password"); role_keys = [key for key in request.data.get("roles", []) if key != "TEAM"]
    if not username or not password:
        return Response({"error":"username & password required"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error":"Username vergeben"}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password)
    profile = Profile.objects.create(user=user, name=username)
    if role_keys:
        roles = Role.objects.filter(key__in=role_keys); profile.roles.set(roles)
    return Response({"message":"registered","user_id":user.id,"profile_id":profile.id})

# --- Profiles/Roles ---
class RoleViewSet(viewsets.ModelViewSet):
    queryset=Role.objects.all(); serializer_class=RoleSerializer; permission_classes=[permissions.IsAuthenticated]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset=Profile.objects.select_related("user").prefetch_related("roles").all()
    serializer_class=ProfileSerializer; permission_classes=[permissions.IsAuthenticated]

    @action(detail=False, methods=["GET"])
    def me(self, request):
        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="search")
    def search(self, request):
        term = (request.query_params.get("q") or "").strip()
        if not term:
            return Response([])
        qs = (
            Profile.objects.select_related("user")
            .prefetch_related("roles")
            .filter(
                Q(name__icontains=term)
                | Q(user__username__icontains=term)
                | Q(city__icontains=term)
                | Q(genre__icontains=term)
            )
            .order_by("name", "user__username")[:10]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated, IsTeam])
    def lock(self, request, pk=None):
        profile = self.get_object()
        locked = _bool_param(request.data.get("locked"), True)
        user = profile.user
        user.is_active = not locked
        user.save(update_fields=["is_active"])
        return Response({"locked": locked})

    @action(detail=True, methods=["POST"], url_path="team-role", permission_classes=[permissions.IsAuthenticated, IsTeam])
    def team_role(self, request, pk=None):
        profile = self.get_object()
        should_add = _bool_param(request.data.get("add"), True)
        team_role, _ = Role.objects.get_or_create(key="TEAM", defaults={"key": "TEAM"})
        if should_add:
            profile.roles.add(team_role)
        else:
            profile.roles.remove(team_role)
        return Response({"is_team_member": profile.roles.filter(key="TEAM").exists()})

# --- Examples/Requests ---
class ExampleViewSet(viewsets.ModelViewSet):
    queryset=Example.objects.all(); serializer_class=ExampleSerializer; permission_classes=[permissions.IsAuthenticated]

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class=RequestSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self):
        me=self.request.user.profile
        return Request.objects.filter(Q(sender=me)|Q(receiver=me)).order_by("-created_at")

    @action(detail=False, methods=["GET"], url_path="team-open", permission_classes=[permissions.IsAuthenticated, IsTeam])
    def team_open(self, request):
        qs = Request.objects.filter(status="OPEN").order_by("-created_at")[:25]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

# --- Chat ---
class ChatThreadViewSet(viewsets.ModelViewSet):
    queryset = ChatThread.objects.all()
    serializer_class = ChatThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        me = self.request.user.profile
        return (
            ChatThread.objects
            .filter(Q(a=me) | Q(b=me))
            .annotate(last_activity=Coalesce(Max("messages__created_at"), "created_at"))
            .select_related("a__user", "b__user")
            .prefetch_related("messages__sender__user")
            .order_by("-last_activity", "-created_at")
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="send")
    def send(self, request, pk=None):
        me = request.user.profile
        thread = self.get_object()
        data = {"thread": thread.id, "text": request.data.get("text","")}
        msg = ChatMessage.objects.create(thread=thread, sender=me, text=data["text"])
        ser = ChatMessageSerializer(msg)
        return Response(ser.data)
    @action(detail=False, methods=["post"], url_path="ensure")
    def ensure(self, request):
        me = request.user.profile
        other = get_object_or_404(Profile, id=request.data.get("profile_id"))
        t = (ChatThread.objects
            .filter((Q(a=me) & Q(b=other)) | (Q(a=other) & Q(b=me)))
        .first())
        if not t:
            t = ChatThread.objects.create(a=me, b=other)
        return Response(ChatThreadSerializer(t).data)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all().order_by("-created_at")
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        me = self.request.user.profile
        instance = serializer.save(sender=me)
        if instance.sender_id == me.id and not instance.read:
            instance.read = True
            instance.save(update_fields=["read"])
# --- Team only ---
def _bool_param(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"1", "true", "yes", "on"}

class ProjectPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

def _parse_date_param(value):
    if not value:
        return None
    dt = parse_date(value)
    return dt


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related("participants").order_by("-created_at")
    serializer_class=ProjectSerializer
    pagination_class = ProjectPagination

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsTeam()]

    def _base_queryset(self):
        qs = Project.objects.prefetch_related("participants").order_by("-created_at")
        me = self.request.user.profile
        if me.roles.filter(key="TEAM").exists():
            return qs
        return qs.filter(participants=me)

    def _apply_visibility_filters(self, qs):
        include_archived = _bool_param(self.request.query_params.get("include_archived"))
        include_done = _bool_param(self.request.query_params.get("include_done"))
        archived_only = _bool_param(self.request.query_params.get("archived_only"))
        if archived_only:
            qs = qs.filter(is_archived=True)
        elif not include_archived:
            qs = qs.filter(is_archived=False)
        if not include_done:
            qs = qs.exclude(status="DONE")
        return qs

    def _apply_search_filters(self, qs):
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        participant = self.request.query_params.get("participant")
        if participant:
            qs = qs.filter(participants__id=participant)
        status = self.request.query_params.get("status")
        if status:
            statuses = [s.strip().upper() for s in status.split(",") if s.strip()]
            if statuses and "ALL" not in statuses:
                qs = qs.filter(status__in=statuses)
        ordering = self.request.query_params.get("ordering")
        allowed = {"title", "-title", "status", "-status", "created_at", "-created_at"}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        return qs

    def get_queryset(self):
        qs = self._base_queryset()
        qs = self._apply_visibility_filters(qs)
        qs = self._apply_search_filters(qs)
        return qs.distinct()

    def perform_create(self, serializer):
        project = serializer.save()
        actor = getattr(self.request.user, "profile", None)
        log_activity(
            "project_created",
            f"Projekt erstellt: {project.title}",
            actor=actor,
            severity="INFO",
            project=project,
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        previous_status = instance.status
        project = serializer.save()
        actor = getattr(self.request.user, "profile", None)
        if previous_status != project.status:
            severity = "SUCCESS" if project.status == "DONE" else "INFO"
            log_activity(
                "project_status_updated",
                f"Projektstatus aktualisiert: {project.title}",
                description=f"{previous_status} -> {project.status}",
                actor=actor,
                severity=severity,
                project=project,
            )

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.archived_at = timezone.now()
        instance.save(update_fields=["is_archived", "archived_at"])
        actor = getattr(self.request.user, "profile", None)
        log_activity(
            "project_archived",
            f"Projekt archiviert: {instance.title}",
            actor=actor,
            severity="WARNING",
            project=instance,
        )

    @action(detail=False, methods=["GET"], url_path="summary")
    def summary(self, request):
        qs = self._base_queryset()
        total = qs.count()
        archived = qs.filter(is_archived=True).count()
        completed = qs.filter(status="DONE").count()
        active = qs.filter(is_archived=False).exclude(status="DONE").count()
        by_status = {
            row["status"]: row["c"]
            for row in qs.values("status").annotate(c=Count("id"))
        }
        return Response(
            {
                "total": total,
                "archived": archived,
                "done": completed,
                "active": active,
                "by_status": by_status,
            }
        )

    @action(detail=False, methods=["GET"], url_path="export")
    def export(self, request):
        qs = self._apply_search_filters(self._apply_visibility_filters(self._base_queryset()))
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["Projekt", "Status", "Teilnehmer", "Erstellt am"])
        for project in qs:
            participants = ", ".join(
                getattr(p, "name", "") or p.user.username for p in project.participants.all()
            )
            writer.writerow([project.title, project.status, participants, project.created_at.isoformat()])
        response = HttpResponse(buffer.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="projects.csv"'
        return response

class TaskViewSet(viewsets.ModelViewSet):
    queryset=Task.objects.all().order_by("-created_at")
    serializer_class=TaskSerializer
    permission_classes=[permissions.IsAuthenticated, IsTeam]

    def _base_queryset(self):
        return Task.objects.select_related("project", "assignee__user").order_by("-created_at")

    def _apply_visibility_filters(self, qs):
        include_archived = _bool_param(self.request.query_params.get("include_archived"))
        include_done = _bool_param(self.request.query_params.get("include_done"))
        archived_only = _bool_param(self.request.query_params.get("archived_only"))
        if archived_only:
            qs = qs.filter(is_archived=True)
        elif not include_archived:
            qs = qs.filter(is_archived=False)
        if not include_done:
            qs = qs.exclude(status="DONE")
        return qs

    def get_queryset(self):
        qs = self._base_queryset()
        project_id = self.request.query_params.get("project")
        status = self.request.query_params.get("status")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if status:
            statuses = [s.strip().upper() for s in status.split(",") if s.strip()]
            if statuses and "ALL" not in statuses:
                qs = qs.filter(status__in=statuses)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(project__title__icontains=search))
        assignee = self.request.query_params.get("assignee")
        if assignee:
            qs = qs.filter(assignee_id=assignee)
        priority = self.request.query_params.get("priority")
        if priority:
            priorities = [p.strip().upper() for p in priority.split(",") if p.strip()]
            if priorities and "ALL" not in priorities:
                qs = qs.filter(priority__in=priorities)
        due_state = self.request.query_params.get("due_state")
        if due_state == "none":
            qs = qs.filter(due_date__isnull=True)
        else:
            due_before = _parse_date_param(self.request.query_params.get("due_before"))
            if due_before:
                qs = qs.filter(due_date__lte=due_before)
            due_after = _parse_date_param(self.request.query_params.get("due_after"))
            if due_after:
                qs = qs.filter(due_date__gte=due_after)
        ordering = self.request.query_params.get("ordering")
        allowed = {"due_date", "-due_date", "priority", "-priority", "created_at", "-created_at"}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        return self._apply_visibility_filters(qs)

    def _log_overdue_if_needed(self, task):
        if not task.due_date or task.status == "DONE":
            return
        if task.due_date >= timezone.now().date():
            return
        exists = ActivityEntry.objects.filter(
            event_type="task_overdue",
            task=task,
            metadata__due_date=str(task.due_date),
        ).exists()
        if not exists:
            log_activity(
                "task_overdue",
                f"Deadline verpasst: {task.title}",
                description=f"Fällig am {task.due_date}",
                severity="DANGER",
                task=task,
                project=task.project,
                metadata={"due_date": str(task.due_date)},
            )

    def perform_create(self, serializer):
        task = serializer.save()
        actor = getattr(self.request.user, "profile", None)
        log_activity(
            "task_created",
            f"Task erstellt: {task.title}",
            actor=actor,
            severity="INFO",
            task=task,
            project=task.project,
        )
        self._log_overdue_if_needed(task)

    def perform_update(self, serializer):
        instance = self.get_object()
        prev_status = instance.status
        prev_priority = instance.priority
        task = serializer.save()
        actor = getattr(self.request.user, "profile", None)
        if prev_status != task.status:
            severity = "SUCCESS" if task.status == "DONE" else "INFO"
            event = "task_completed" if task.status == "DONE" else "task_status_updated"
            log_activity(
                event,
                f"Taskstatus aktualisiert: {task.title}",
                description=f"{prev_status} -> {task.status}",
                actor=actor,
                severity=severity,
                task=task,
                project=task.project,
            )
        if prev_priority != task.priority:
            log_activity(
                "task_priority_updated",
                f"Priorität geändert: {task.title}",
                description=f"{prev_priority} -> {task.priority}",
                actor=actor,
                severity="INFO",
                task=task,
                project=task.project,
            )
        self._log_overdue_if_needed(task)

    def perform_destroy(self, instance):
        instance.is_archived = True
        instance.archived_at = timezone.now()
        instance.save(update_fields=["is_archived", "archived_at"])
        actor = getattr(self.request.user, "profile", None)
        log_activity(
            "task_archived",
            f"Task archiviert: {instance.title}",
            actor=actor,
            severity="WARNING",
            task=instance,
            project=instance.project,
        )

    @action(detail=False, methods=["GET"], url_path="overdue")
    def overdue(self, request):
        today = timezone.now().date()
        qs = (
            self._base_queryset()
            .filter(is_archived=False, due_date__lt=today)
            .exclude(status="DONE")
            .order_by("due_date")[:15]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["GET"], url_path="upcoming")
    def upcoming(self, request):
        days = int(request.query_params.get("days", 7))
        limit = min(max(int(request.query_params.get("limit", 8)), 1), 25)
        start = timezone.now().date()
        end = start + timedelta(days=days)
        qs = (
            self._base_queryset()
            .filter(is_archived=False, due_date__gte=start, due_date__lte=end)
            .exclude(status="DONE")
            .order_by("due_date", "priority")[:limit]
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ProjectAttachmentViewSet(viewsets.ModelViewSet):
    queryset = ProjectAttachment.objects.select_related("project", "uploaded_by__user").order_by("-created_at")
    serializer_class = ProjectAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsTeamOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        me = getattr(self.request.user, "profile", None)
        if me and not me.roles.filter(key="TEAM").exists():
            qs = qs.filter(project__participants=me)
        return qs

    def perform_create(self, serializer):
        attachment = serializer.save(uploaded_by=self.request.user.profile)
        log_activity(
            "project_attachment_added",
            f"Projektanhang: {attachment.project.title}",
            description=attachment.label or attachment.file.name,
            actor=self.request.user.profile,
            severity="INFO",
            project=attachment.project,
        )

    def perform_destroy(self, instance):
        log_activity(
            "project_attachment_removed",
            f"Projektanhang entfernt: {instance.project.title}",
            description=instance.label or instance.file.name,
            actor=getattr(self.request.user, "profile", None),
            severity="WARNING",
            project=instance.project,
        )
        super().perform_destroy(instance)


class TaskAttachmentViewSet(viewsets.ModelViewSet):
    queryset = TaskAttachment.objects.select_related("task__project", "uploaded_by__user").order_by("-created_at")
    serializer_class = TaskAttachmentSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated, IsTeam]

    def get_queryset(self):
        qs = super().get_queryset()
        task_id = self.request.query_params.get("task")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs

    def perform_create(self, serializer):
        attachment = serializer.save(uploaded_by=self.request.user.profile)
        log_activity(
            "task_attachment_added",
            f"Taskanhang: {attachment.task.title}",
            description=attachment.label or attachment.file.name,
            actor=self.request.user.profile,
            severity="INFO",
            task=attachment.task,
            project=attachment.task.project,
        )

    def perform_destroy(self, instance):
        log_activity(
            "task_attachment_removed",
            f"Taskanhang entfernt: {instance.task.title}",
            description=instance.label or instance.file.name,
            actor=getattr(self.request.user, "profile", None),
            severity="WARNING",
            task=instance.task,
            project=instance.task.project,
        )
        super().perform_destroy(instance)


class TaskCommentViewSet(viewsets.ModelViewSet):
    queryset = TaskComment.objects.select_related("task__project", "author__user").prefetch_related("mentions__user")
    serializer_class = TaskCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeam]

    def get_queryset(self):
        qs = super().get_queryset()
        task_id = self.request.query_params.get("task")
        if task_id:
            qs = qs.filter(task_id=task_id)
        return qs.order_by("-created_at")

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user.profile)
        log_activity(
            "task_comment",
            f"Kommentar zu {comment.task.title}",
            description=comment.body[:160],
            actor=self.request.user.profile,
            severity="INFO",
            task=comment.task,
            project=comment.task.project,
        )

    def perform_destroy(self, instance):
        log_activity(
            "task_comment_removed",
            f"Kommentar entfernt: {instance.task.title}",
            description=instance.body[:160],
            actor=getattr(self.request.user, "profile", None),
            severity="WARNING",
            task=instance.task,
            project=instance.task.project,
        )
        super().perform_destroy(instance)

    @action(detail=False, methods=["GET"], url_path="summary")
    def summary(self, request):
        qs = self._base_queryset()
        total = qs.count()
        archived = qs.filter(is_archived=True).count()
        completed = qs.filter(status="DONE").count()
        active = qs.filter(is_archived=False).exclude(status="DONE").count()
        by_status = {
            row["status"]: row["c"]
            for row in qs.values("status").annotate(c=Count("id"))
        }
        return Response(
            {
                "total": total,
                "archived": archived,
                "done": completed,
                "active": active,
                "by_status": by_status,
            }
        )

class ContractViewSet(viewsets.ModelViewSet):
    queryset=Contract.objects.all(); serializer_class=ContractSerializer
    def get_permissions(self):
        if self.request.method in ["POST","PUT","PATCH","DELETE"]:
            return [IsTeam()]
        return [permissions.IsAuthenticated()]

class PaymentViewSet(viewsets.ModelViewSet):
    queryset=Payment.objects.all(); serializer_class=PaymentSerializer
    def get_permissions(self):
        if self.request.method in ["POST","PUT","PATCH","DELETE"]:
            return [IsTeam()]
        return [permissions.IsAuthenticated()]

class ReleaseViewSet(viewsets.ModelViewSet):
    queryset=Release.objects.all(); serializer_class=ReleaseSerializer; permission_classes=[permissions.IsAuthenticated]

class EventViewSet(viewsets.ModelViewSet):
    queryset=Event.objects.all(); serializer_class=EventSerializer
    def get_permissions(self):
        if self.request.method in ["POST","PUT","PATCH","DELETE"]:
            return [IsTeam()]
        return [permissions.IsAuthenticated()]

class BookingViewSet(viewsets.ModelViewSet):
    queryset=Booking.objects.all(); serializer_class=BookingSerializer; permission_classes=[permissions.IsAuthenticated]


class NewsPostViewSet(viewsets.ModelViewSet):
    queryset = NewsPost.objects.select_related("author__user").order_by("-created_at")
    serializer_class = NewsPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        me = getattr(self.request.user, "profile", None)
        if not me or not me.roles.filter(key="TEAM").exists():
            qs = qs.filter(is_published=True)
        return qs

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsTeam()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    @action(detail=True, methods=["POST"], permission_classes=[permissions.IsAuthenticated, IsTeam])
    def publish(self, request, pk=None):
        post = self.get_object()
        publish = _bool_param(request.data.get("publish"), True)
        post.is_published = publish
        post.save(update_fields=["is_published"])
        return Response({"is_published": publish})


class ActivityFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsTeam]

    def get(self, request):
        limit = int(request.query_params.get("limit", 100))
        limit = max(1, min(limit, 200))
        self._ensure_overdue_entries()
        qs = (
            ActivityEntry.objects.select_related("actor__user", "project", "task")
            .order_by("-created_at")[:limit]
        )
        serializer = ActivityEntrySerializer(qs, many=True)
        return Response(serializer.data)

    def _ensure_overdue_entries(self):
        today = timezone.now().date()
        overdue_tasks = (
            Task.objects.select_related("project")
            .filter(is_archived=False, due_date__lt=today)
            .exclude(status="DONE")
        )
        for task in overdue_tasks:
            exists = ActivityEntry.objects.filter(
                event_type="task_overdue",
                task=task,
                metadata__due_date=str(task.due_date),
            ).exists()
            if not exists:
                log_activity(
                    "task_overdue",
                    f"Deadline verpasst: {task.title}",
                    description=f"Fällig am {task.due_date}",
                    severity="DANGER",
                    task=task,
                    project=task.project,
                    metadata={"due_date": str(task.due_date)},
                )

# --- Stats (rollenbasiert) ---
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def stats(request):
    counts = {k:0 for k,_ in ROLE_CHOICES}
    for row in Role.objects.annotate(c=Count("profile")).values("key","c"):
        counts[row["key"]] = row["c"]
    me = request.user.profile
    if me.roles.filter(key="TEAM").exists():
        open_requests = Request.objects.filter(status="OPEN").count()
        active_contracts = Contract.objects.filter(status="ACTIVE").count()
        due_payments = Payment.objects.filter(status="DUE").count()
    else:
        open_requests = Request.objects.filter(Q(sender=me)|Q(receiver=me), status="OPEN").count()
        active_contracts = Contract.objects.filter(profile=me, status="ACTIVE").count()
        due_payments = Payment.objects.filter(profile=me, status="DUE").count()
    return Response({"roles":counts,"open_requests":open_requests,"active_contracts":active_contracts,"due_payments":due_payments})

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, IsTeam])
def admin_overview(request):
    today = timezone.now().date()
    last_week = timezone.now() - timedelta(days=7)
    total_users = Profile.objects.count()
    locked_users = Profile.objects.filter(user__is_active=False).count()
    team_members = Profile.objects.filter(roles__key="TEAM").distinct().count()
    new_users = Profile.objects.filter(created_at__gte=last_week).count()
    active_projects = Project.objects.filter(is_archived=False).count()
    overdue_tasks = (
        Task.objects.filter(is_archived=False, due_date__lt=today)
        .exclude(status="DONE")
        .count()
    )
    return Response(
        {
            "total_users": total_users,
            "locked_users": locked_users,
            "team_members": team_members,
            "new_users_last_7_days": new_users,
            "active_projects": active_projects,
            "overdue_tasks": overdue_tasks,
        }
    )

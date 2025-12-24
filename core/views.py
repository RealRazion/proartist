import csv
import io
import os
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count, Max, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.dateparse import parse_date
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import permissions, viewsets, status
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
    Song,
    SongVersion,
    GrowProGoal,
    GrowProUpdate,
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
    GrowProGoalSerializer,
    GrowProUpdateSerializer,
    SongSerializer,
    SongVersionSerializer,
    TaskAttachmentSerializer,
    TaskCommentSerializer,
    TaskSerializer,
)
from .utils import log_activity
from .notifications import send_notification_email
from .realtime import notify_project_event, notify_task_event
from .automation import send_task_reminders

# --- Auth/Register ---
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsTeam])
def register(request):
    username = request.data.get("username"); email = request.data.get("email")
    password = request.data.get("password")
    # Nur Nicht-Team-Rollen erlauben, TEAM wird ignoriert
    allowed_roles = {"ARTIST", "PROD", "VIDEO", "MERCH", "MKT", "LOC"}
    role_keys = [key for key in request.data.get("roles", []) if key in allowed_roles]
    if not username or not password:
        return Response({"error":"username & password required"}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"error":"Username vergeben"}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password)
    profile = Profile.objects.create(user=user, name=username)
    if role_keys:
        roles = Role.objects.filter(key__in=role_keys); profile.roles.set(roles)
    return Response({"message":"registered","user_id":user.id,"profile_id":profile.id})

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsTeam])
def invite_user(request):
    email = (request.data.get("email") or "").strip().lower()
    name = (request.data.get("name") or "").strip()
    role_keys = request.data.get("roles") or []
    if not email:
        return Response({"detail": "email required"}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return Response({"detail": "email already exists"}, status=400)
    base_username = email.split("@")[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        counter += 1
        username = f"{base_username}{counter}"
    user = User.objects.create_user(username=username, email=email)
    user.set_unusable_password()
    user.save(update_fields=["password"])
    profile = Profile.objects.create(user=user, name=name or username)
    if role_keys:
        roles = Role.objects.filter(key__in=role_keys)
        profile.roles.set(roles)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
    link = f"{frontend_url}/set-password?uid={uid}&token={token}"
    send_notification_email(
        "Dein ProArtist Zugang",
        f"Hallo,\n\nbitte setze dein Passwort über diesen Link:\n{link}\n\nViele Grüße",
        [email],
    )
    return Response({"id": profile.id, "email": email, "username": username, "invite_link": link})

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def set_password(request):
    uid = request.data.get("uid")
    token = request.data.get("token")
    password = request.data.get("password")
    if not uid or not token or not password:
        return Response({"detail": "missing data"}, status=400)
    if len(password) < 8:
        return Response({"detail": "password too short"}, status=400)
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except Exception:
        return Response({"detail": "invalid link"}, status=400)
    if not default_token_generator.check_token(user, token):
        return Response({"detail": "invalid link"}, status=400)
    user.set_password(password)
    user.save(update_fields=["password"])
    return Response({"detail": "password set"})

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

# --- Paginierung ---
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


# --- Examples/Requests ---
class ExampleViewSet(viewsets.ModelViewSet):
    queryset=Example.objects.all(); serializer_class=ExampleSerializer; permission_classes=[permissions.IsAuthenticated]

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class=RequestSerializer; permission_classes=[permissions.IsAuthenticated]; pagination_class = StandardPagination
    def get_queryset(self):
        me=self.request.user.profile
        qs = Request.objects.filter(Q(sender=me)|Q(receiver=me))
        status_param = self.request.query_params.get("status")
        if status_param and status_param.upper() != "ALL":
            qs = qs.filter(status=status_param.upper())
        req_type = self.request.query_params.get("type")
        if req_type and req_type.upper() != "ALL":
            qs = qs.filter(req_type=req_type.upper())
        search = (self.request.query_params.get("search") or "").strip()
        if search:
            qs = qs.filter(
                Q(sender__name__icontains=search)
                | Q(receiver__name__icontains=search)
                | Q(message__icontains=search)
            )
        return qs.order_by("-created_at")

    @action(detail=False, methods=["GET"], url_path="team-open", permission_classes=[permissions.IsAuthenticated, IsTeam])
    def team_open(self, request):
        qs = Request.objects.filter(status="OPEN").order_by("-created_at")[:25]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], url_path="accept", permission_classes=[permissions.IsAuthenticated, IsTeam])
    def accept(self, request, pk=None):
        req = self.get_object()
        req.status = "ACCEPTED"
        req.save(update_fields=["status"])
        log_activity(
            "request_accepted",
            f"Request angenommen: {req.sender} -> {req.receiver}",
            actor=getattr(request.user, "profile", None),
            severity="SUCCESS",
        )
        return Response({"status": req.status})

    @action(detail=True, methods=["POST"], url_path="decline", permission_classes=[permissions.IsAuthenticated, IsTeam])
    def decline(self, request, pk=None):
        req = self.get_object()
        req.status = "DECLINED"
        req.save(update_fields=["status"])
        log_activity(
            "request_declined",
            f"Request abgelehnt: {req.sender} -> {req.receiver}",
            actor=getattr(request.user, "profile", None),
            severity="WARNING",
        )
        return Response({"status": req.status})

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


def _profile_emails(profiles, exclude_ids=None):
    emails = []
    exclude_ids = set(exclude_ids or [])
    for profile in profiles:
        if profile.id in exclude_ids:
            continue
        user = getattr(profile, "user", None)
        email = getattr(user, "email", None)
        if email:
            emails.append(email)
    return emails


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related("participants", "owners").order_by("-created_at")
    serializer_class=ProjectSerializer
    pagination_class = ProjectPagination

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsTeam()]

    def _base_queryset(self):
        qs = Project.objects.prefetch_related("participants", "owners").order_by("-created_at")
        me = self.request.user.profile
        if me.roles.filter(key="TEAM").exists():
            return qs
        return qs.filter(Q(participants=me) | Q(owners=me)).distinct()

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
        owner = self.request.query_params.get("owner")
        if owner:
            qs = qs.filter(owners__id=owner)
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
        notify_project_event(project, "created")

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
        notify_project_event(project, "updated")

    def perform_destroy(self, instance):
        actor = getattr(self.request.user, "profile", None)
        notify_project_event(instance, "deleted")
        log_activity(
            "project_deleted",
            f"Projekt gelöscht: {instance.title}",
            actor=actor,
            severity="DANGER",
            project=instance,
        )
        instance.delete()

    @action(detail=True, methods=["POST"], url_path="archive")
    def archive(self, request, pk=None):
        project = self.get_object()
        if not project.is_archived:
            project.is_archived = True
            project.archived_at = timezone.now()
            project.save(update_fields=["is_archived", "archived_at"])
            actor = getattr(self.request.user, "profile", None)
            log_activity(
                "project_archived",
                f"Projekt archiviert: {project.title}",
                actor=actor,
                severity="WARNING",
                project=project,
            )
            notify_project_event(project, "archived")
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], url_path="delete")
    def delete_project(self, request, pk=None):
        project = self.get_object()
        self.perform_destroy(project)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["GET"], url_path="timeline")
    def timeline(self, request):
        start = _parse_date_param(request.query_params.get("start")) or timezone.now().date()
        end = _parse_date_param(request.query_params.get("end")) or (start + timedelta(days=60))
        qs = (
            self._base_queryset()
            .filter(created_at__date__lte=end)
            .filter(Q(archived_at__isnull=True) | Q(archived_at__date__gte=start))
        )
        serializer = self.get_serializer(qs, many=True)
        return Response({"start": start, "end": end, "results": serializer.data})

    @action(detail=False, methods=["GET"], url_path="summary")
    def summary(self, request):
        qs = self._base_queryset()
        total = qs.count()
        archived = qs.filter(is_archived=True).count()
        completed = qs.filter(status="DONE").count()
        active = qs.exclude(status="DONE").count()
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
    pagination_class = StandardPagination

    def _base_queryset(self):
        return (
            Task.objects.select_related("project")
            .prefetch_related("stakeholders__user", "assignees__user")
            .order_by("-created_at")
        )

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
            ids = [pk.strip() for pk in str(assignee).split(",") if pk.strip()]
            if ids:
                qs = qs.filter(assignees__id__in=ids)
        stakeholder = self.request.query_params.get("stakeholder")
        if stakeholder:
            qs = qs.filter(stakeholders__id=stakeholder)
        priority = self.request.query_params.get("priority")
        if priority:
            priorities = [p.strip().upper() for p in priority.split(",") if p.strip()]
            if priorities and "ALL" not in priorities:
                qs = qs.filter(priority__in=priorities)
        task_type = self.request.query_params.get("task_type")
        if task_type:
            types = [t.strip().upper() for t in task_type.split(",") if t.strip()]
            if types and "ALL" not in types:
                qs = qs.filter(task_type__in=types)
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
        return self._apply_visibility_filters(qs).distinct()

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
        if task.status == "DONE" and not task.completed_at:
            task.completed_at = timezone.now()
            task.save(update_fields=["completed_at"])
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
        notify_task_event(task, "created")
        recipients = _profile_emails(task.assignees.all(), exclude_ids={getattr(actor, "id", None)})
        if recipients:
            send_notification_email(
                f"Neuer Task: {task.title}",
                f"Dir wurde ein neuer Task zugewiesen.\n\nTitel: {task.title}\nProjekt: {task.project.title if task.project else 'Kein Projekt'}\nStatus: {task.status}",
                recipients,
            )

    def perform_update(self, serializer):
        instance = self.get_object()
        prev_status = instance.status
        prev_priority = instance.priority
        previous_assignees = set(instance.assignees.values_list("id", flat=True))
        task = serializer.save()
        if prev_status != task.status:
            if task.status == "DONE" and not task.completed_at:
                task.completed_at = timezone.now()
                task.save(update_fields=["completed_at"])
            elif prev_status == "DONE" and task.status != "DONE":
                task.completed_at = None
                task.save(update_fields=["completed_at"])
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
        self._notify_new_assignees(previous_assignees, task, actor)
        self._log_overdue_if_needed(task)
        notify_task_event(task, "updated")

    def perform_destroy(self, instance):
        actor = getattr(self.request.user, "profile", None)
        notify_task_event(instance, "deleted")
        log_activity(
            "task_deleted",
            f"Task gelöscht: {instance.title}",
            actor=actor,
            severity="DANGER",
            task=instance,
            project=instance.project,
        )
        instance.delete()

    @action(detail=True, methods=["POST"], url_path="archive")
    def archive(self, request, pk=None):
        task = self.get_object()
        if not task.is_archived:
            task.is_archived = True
            task.archived_at = timezone.now()
            task.save(update_fields=["is_archived", "archived_at"])
            actor = getattr(self.request.user, "profile", None)
            log_activity(
                "task_archived",
                f"Task archiviert: {task.title}",
                actor=actor,
                severity="WARNING",
                task=task,
                project=task.project,
            )
        notify_task_event(task, "archived")
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"], url_path="delete")
    def delete_task(self, request, pk=None):
        task = self.get_object()
        self.perform_destroy(task)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _notify_new_assignees(self, previous_assignees, task, actor):
        current_ids = set(task.assignees.values_list("id", flat=True))
        new_ids = current_ids - set(previous_assignees or [])
        if not new_ids:
            return
        new_profiles = task.assignees.filter(id__in=new_ids)
        recipients = _profile_emails(new_profiles, exclude_ids={getattr(actor, "id", None)})
        if not recipients:
            return
        send_notification_email(
            f"Neuer Task: {task.title}",
            f"Dir wurde ein Task zugewiesen.\n\nTitel: {task.title}\nStatus: {task.status}\nFällig: {task.due_date or 'Kein Termin'}",
            recipients,
        )

    @action(detail=False, methods=["GET"], url_path="calendar")
    def calendar(self, request):
        start = _parse_date_param(request.query_params.get("start")) or timezone.now().date()
        end_param = _parse_date_param(request.query_params.get("end")) or (start + timedelta(days=30))
        qs = (
            self._base_queryset()
            .filter(due_date__isnull=False, due_date__gte=start, due_date__lte=end_param)
        )
        serializer = self.get_serializer(qs, many=True)
        return Response({"start": start, "end": end_param, "results": serializer.data})
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
        by_type = {
            row["task_type"]: row["c"]
            for row in qs.values("task_type").annotate(c=Count("id"))
        }
        return Response(
            {
                "total": total,
                "archived": archived,
                "done": completed,
                "active": active,
                "by_status": by_status,
                "by_type": by_type,
            }
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
        mentions = comment.mentions.exclude(id=comment.author_id).select_related("user")
        recipients = _profile_emails(mentions)
        if recipients:
            send_notification_email(
                f"Neue Erwähnung in {comment.task.title}",
                f"{comment.author.name or comment.author.user.username} hat dich in einem Task-Kommentar erwähnt.\n\nKommentar:\n{comment.body}",
                recipients,
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


class SongViewSet(viewsets.ModelViewSet):
    serializer_class = SongSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = Song.objects.select_related("profile__user", "project").prefetch_related("versions")
        me = getattr(self.request.user, "profile", None)
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))
        status_param = self.request.query_params.get("status")
        if status_param:
            statuses = [s.strip().upper() for s in status_param.split(",") if s.strip()]
            if statuses and "ALL" not in statuses:
                qs = qs.filter(status__in=statuses)
        if me and not me.roles.filter(key="TEAM").exists():
            qs = qs.filter(profile=me)
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        project_id = self.request.query_params.get("project")
        if project_id:
            qs = qs.filter(project_id=project_id)
        ordering = self.request.query_params.get("ordering")
        allowed = {"created_at", "-created_at", "title", "-title", "status", "-status"}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-created_at")
        return qs

    def perform_create(self, serializer):
        song = serializer.save(profile=self.request.user.profile)
        log_activity(
            "song_created",
            f"Song angelegt: {song.title}",
            actor=self.request.user.profile,
            severity="INFO",
        )

    def perform_update(self, serializer):
        instance = self.get_object()
        me = self.request.user.profile
        data = serializer.validated_data
        if not me.roles.filter(key="TEAM").exists():
            data.pop("project", None)
        song = serializer.save()
        log_activity(
            "song_updated",
            f"Song aktualisiert: {song.title}",
            actor=me,
            severity="INFO",
            project=song.project,
        )

    def perform_destroy(self, instance):
        log_activity(
            "song_deleted",
            f"Song gelöscht: {instance.title}",
            actor=getattr(self.request.user, "profile", None),
            severity="WARNING",
            project=instance.project,
        )
        super().perform_destroy(instance)

    def update(self, request, *args, **kwargs):
        song = self.get_object()
        me = request.user.profile
        if song.profile_id != me.id and not me.roles.filter(key="TEAM").exists():
            return Response({"detail": "Nicht erlaubt"}, status=403)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        song = self.get_object()
        me = request.user.profile
        if song.profile_id != me.id and not me.roles.filter(key="TEAM").exists():
            return Response({"detail": "Nicht erlaubt"}, status=403)
        return super().destroy(request, *args, **kwargs)


class SongVersionViewSet(viewsets.ModelViewSet):
    serializer_class = SongVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = SongVersion.objects.select_related("song__profile__user", "song__project")
        song_id = self.request.query_params.get("song")
        if song_id:
            qs = qs.filter(song_id=song_id)
        ordering = self.request.query_params.get("ordering")
        allowed = {"created_at", "-created_at", "version_number", "-version_number"}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        else:
            qs = qs.order_by("-created_at")
        return qs

    def perform_create(self, serializer):
        song = serializer.validated_data["song"]
        me = self.request.user.profile
        if song.profile_id != me.id and not me.roles.filter(key="TEAM").exists():
            return Response({"detail": "Nicht erlaubt"}, status=403)
        version = serializer.save()
        log_activity(
            "song_version_created",
            f"Neue Version: {song.title} v{version.version_number}",
            actor=me,
            severity="INFO",
            project=song.project,
        )


class GrowProGoalViewSet(viewsets.ModelViewSet):
    serializer_class = GrowProGoalSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = GrowProGoal.objects.select_related("profile__user", "created_by__user").prefetch_related("updates__created_by__user")
        me = self.request.user.profile
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(metric__icontains=search) | Q(description__icontains=search))
        if not me.roles.filter(key="TEAM").exists():
            qs = qs.filter(profile=me)
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        status_param = self.request.query_params.get("status")
        if status_param:
            statuses = [s.strip().upper() for s in status_param.split(",") if s.strip()]
            if statuses and "ALL" not in statuses:
                qs = qs.filter(status__in=statuses)
        ordering = self.request.query_params.get("ordering")
        allowed = {
            "due_date",
            "-due_date",
            "last_logged_at",
            "-last_logged_at",
            "updated_at",
            "-updated_at",
            "created_at",
            "-created_at",
        }
        if ordering in allowed:
            qs = qs.order_by(ordering, "-created_at")
        else:
            qs = qs.order_by("due_date", "-created_at")
        return qs

    def perform_create(self, serializer):
        me = self.request.user.profile
        data = serializer.validated_data
        if not me.roles.filter(key="TEAM").exists():
            data["profile"] = me
            data["created_by"] = me
        goal = serializer.save(created_by=me)
        log_activity(
            "growpro_created",
            f"GrowPro Ziel: {goal.title}",
            actor=me,
            severity="INFO",
            project=goal.profile.projects.first() if goal.profile else None,
        )

    def perform_update(self, serializer):
        goal = serializer.save()
        log_activity(
            "growpro_updated",
            f"GrowPro Ziel aktualisiert: {goal.title}",
            actor=getattr(self.request.user, "profile", None),
            severity="INFO",
        )

    @action(detail=True, methods=["POST"], url_path="log", permission_classes=[permissions.IsAuthenticated])
    def log_value(self, request, pk=None):
        goal = self.get_object()
        me = request.user.profile
        if goal.profile_id != me.id and not me.roles.filter(key="TEAM").exists():
            return Response({"detail": "Nicht erlaubt"}, status=403)
        try:
            value = float(request.data.get("value"))
        except (TypeError, ValueError):
            return Response({"detail": "Wert fehlt oder ist ungültig"}, status=400)
        note = request.data.get("note", "")
        update = GrowProUpdate.objects.create(goal=goal, value=value, note=note, created_by=me)
        goal.current_value = value
        goal.last_logged_at = timezone.now()
        goal.save(update_fields=["current_value", "last_logged_at", "updated_at"])
        severity = "DANGER" if (goal.due_date and goal.due_date < timezone.now().date()) else "SUCCESS"
        log_activity(
            "growpro_logged",
            f"GrowPro Update: {goal.title}",
            description=note[:200] if note else "",
            actor=me,
            severity=severity,
            project=goal.profile.projects.first() if goal.profile else None,
            metadata={"value": value, "goal_id": goal.id},
        )
        return Response(GrowProUpdateSerializer(update).data)

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
        types_param = request.query_params.get("types")
        types = None
        if types_param:
            types = [t.strip() for t in types_param.split(",") if t.strip()]
        self._ensure_overdue_entries()
        qs = (
            ActivityEntry.objects.select_related("actor__user", "project", "task")
            .order_by("-created_at")
        )
        if types:
            qs = qs.filter(event_type__in=types)
        qs = qs[:limit]
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

@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated, IsTeam])
def analytics_summary(request):
    today = timezone.now().date()
    soon_days = int(request.query_params.get("soon_days", 7) or 7)
    soon_days = max(1, min(30, soon_days))
    base_tasks = Task.objects.filter(is_archived=False).exclude(status="DONE")
    active_tasks = base_tasks.count()
    overdue_tasks = base_tasks.filter(due_date__isnull=False, due_date__lt=today).count()
    due_soon_tasks = base_tasks.filter(
        due_date__isnull=False,
        due_date__gte=today,
        due_date__lte=today + timedelta(days=soon_days),
    ).count()
    completed_last_7_days = Task.objects.filter(
        completed_at__isnull=False,
        completed_at__gte=timezone.now() - timedelta(days=7),
    ).count()
    return Response(
        {
            "active_tasks": active_tasks,
            "overdue_tasks": overdue_tasks,
            "due_soon_tasks": due_soon_tasks,
            "completed_last_7_days": completed_last_7_days,
        }
    )

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated, IsTeam])
def run_task_reminders(request):
    days = int(request.data.get("days", 3) or 3)
    days = max(1, min(30, days))
    include_overdue = _bool_param(request.data.get("include_overdue"), True)
    include_due_soon = _bool_param(request.data.get("include_due_soon"), True)
    dry_run = _bool_param(request.data.get("dry_run"), False)
    summary = send_task_reminders(
        days=days,
        include_overdue=include_overdue,
        include_due_soon=include_due_soon,
        dry_run=dry_run,
    )
    summary["days"] = days
    return Response(summary)

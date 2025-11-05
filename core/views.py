from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Q, Count, Max
from django.db.models.functions import Coalesce

from .models import (
    ROLE_CHOICES, Profile, Role, Example, Request, ChatThread, ChatMessage,
    Project, Task, Contract, Payment, Release, Event, Booking
)
from .serializers import (
    ProfileSerializer, RoleSerializer, ExampleSerializer, RequestSerializer,
    ChatThreadSerializer, ChatMessageSerializer, ProjectSerializer, TaskSerializer,
    ContractSerializer, PaymentSerializer, ReleaseSerializer, EventSerializer, BookingSerializer
)
from .permissions import IsTeam

# --- Auth/Register ---
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register(request):
    username = request.data.get("username"); email = request.data.get("email")
    password = request.data.get("password"); role_keys = request.data.get("roles", [])
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
        return Response(ProfileSerializer(request.user.profile).data)

# --- Examples/Requests ---
class ExampleViewSet(viewsets.ModelViewSet):
    queryset=Example.objects.all(); serializer_class=ExampleSerializer; permission_classes=[permissions.IsAuthenticated]

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class=RequestSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self):
        me=self.request.user.profile
        return Request.objects.filter(Q(sender=me)|Q(receiver=me)).order_by("-created_at")

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
class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related("participants").order_by("-created_at")
    serializer_class=ProjectSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsTeam()]

    def get_queryset(self):
        me = self.request.user.profile
        qs = super().get_queryset()
        if me.roles.filter(key="TEAM").exists():
            return qs
        return qs.filter(participants=me)

class TaskViewSet(viewsets.ModelViewSet):
    queryset=Task.objects.all().order_by("-created_at")
    serializer_class=TaskSerializer
    permission_classes=[permissions.IsAuthenticated, IsTeam]

    def get_queryset(self):
        qs = super().get_queryset().select_related("project", "assignee__user")
        project_id = self.request.query_params.get("project")
        status = self.request.query_params.get("status")
        if project_id:
            qs = qs.filter(project_id=project_id)
        if status:
            statuses = [s.strip().upper() for s in status.split(",") if s.strip()]
            if statuses:
                qs = qs.filter(status__in=statuses)
        return qs

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

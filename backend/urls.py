from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    ActivityFeedView,
    BookingViewSet,
    ChatMessageViewSet,
    ChatThreadViewSet,
    ContractViewSet,
    EventViewSet,
    ExampleViewSet,
    GrowProGoalViewSet,
    NewsPostViewSet,
    PaymentViewSet,
    PluginGuideViewSet,
    ProfileViewSet,
    ProjectAttachmentViewSet,
    ProjectViewSet,
    RegistrationRequestViewSet,
    ReleaseViewSet,
    RequestViewSet,
    RoleViewSet,
    SongViewSet,
    SongVersionViewSet,
    TaskAttachmentViewSet,
    TaskCommentViewSet,
    TaskViewSet,
    analytics_summary,
    admin_overview,
    invite_user,
    register,
    run_task_reminders,
    set_password,
    stats,
)

router = routers.DefaultRouter()
router.register(r"roles", RoleViewSet)
router.register(r"profiles", ProfileViewSet)
router.register(r"examples", ExampleViewSet)
router.register(r"requests", RequestViewSet)
router.register(r"threads", ChatThreadViewSet)
router.register(r"messages", ChatMessageViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"registration-requests", RegistrationRequestViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"project-attachments", ProjectAttachmentViewSet, basename="project-attachments")
router.register(r"task-attachments", TaskAttachmentViewSet, basename="task-attachments")
router.register(r"task-comments", TaskCommentViewSet, basename="task-comments")
router.register(r"songs", SongViewSet, basename="songs")
router.register(r"song-versions", SongVersionViewSet, basename="song-versions")
router.register(r"growpro", GrowProGoalViewSet, basename="growpro-goals")
router.register(r"plugin-guides", PluginGuideViewSet, basename="plugin-guides")
router.register(r"contracts", ContractViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"releases", ReleaseViewSet)
router.register(r"events", EventViewSet)
router.register(r"bookings", BookingViewSet)
router.register(r"news", NewsPostViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register/", register),
    path("api/invite/", invite_user),
    path("api/set-password/", set_password),
    path("api/stats/", stats),
    path("api/admin/overview/", admin_overview),
    path("api/analytics/summary/", analytics_summary),
    path("api/automation/task-reminders/", run_task_reminders),
    path("api/activity-feed/", ActivityFeedView.as_view(), name="activity-feed"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

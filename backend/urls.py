from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    ActivityFeedView,
    AutomationRuleViewSet,
    BookingViewSet,
    ChatMessageViewSet,
    ChatThreadViewSet,
    ContractViewSet,
    DailyExpenseViewSet,
    DebtViewSet,
    EventViewSet,
    ExampleViewSet,
    FinanceEntryViewSet,
    FinanceMemberViewSet,
    FinanceProjectViewSet,
    FinanceTipViewSet,
    GrowProGoalViewSet,
    NewsPostViewSet,
    NotificationViewSet,
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
    SystemIntegrationViewSet,
    TaskAttachmentViewSet,
    TaskCommentViewSet,
    TaskViewSet,
    TournamentApplicationViewSet,
    TournamentBattleViewSet,
    TournamentSubmissionViewSet,
    TournamentViewSet,
    TournamentVoteViewSet,
    SearchView,
    analytics_summary,
    admin_overview,
    ArtistEngagementView,
    calendar_export,
    invite_user,
    register,
    verify_registration,
    run_task_reminders,
    set_password,
    stats,
    TeamPointsView,
    api_center_status,
    send_test_email,
)

router = routers.DefaultRouter()
router.register(r"roles", RoleViewSet)
router.register(r"profiles", ProfileViewSet)
router.register(r"notifications", NotificationViewSet, basename="notifications")
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
router.register(r"automation-rules", AutomationRuleViewSet, basename="automation-rules")
router.register(r"system-integrations", SystemIntegrationViewSet, basename="system-integrations")
router.register(r"contracts", ContractViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"finance-projects", FinanceProjectViewSet, basename="finance-projects")
router.register(r"finance-members", FinanceMemberViewSet, basename="finance-members")
router.register(r"finance-entries", FinanceEntryViewSet, basename="finance-entries")
router.register(r"debts", DebtViewSet, basename="debts")
router.register(r"daily-expenses", DailyExpenseViewSet, basename="daily-expenses")
router.register(r"releases", ReleaseViewSet)
router.register(r"events", EventViewSet)
router.register(r"bookings", BookingViewSet)
router.register(r"news", NewsPostViewSet)
router.register(r"finance-tips", FinanceTipViewSet, basename="finance-tips")
router.register(r"tournaments", TournamentViewSet, basename="tournaments")
router.register(r"tournament-applications", TournamentApplicationViewSet, basename="tournament-applications")
router.register(r"tournament-submissions", TournamentSubmissionViewSet, basename="tournament-submissions")
router.register(r"tournament-battles", TournamentBattleViewSet, basename="tournament-battles")
router.register(r"tournament-votes", TournamentVoteViewSet, basename="tournament-votes")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register/", register),
    path("api/verify-registration/", verify_registration),
    path("api/invite/", invite_user),
    path("api/set-password/", set_password),
    path("api/stats/", stats),
    path("api/admin/overview/", admin_overview),
    path("api/admin/dashboard/", admin_overview),
    path("api/analytics/summary/", analytics_summary),
    path("api/api-center/status/", api_center_status),
    path("api/automation/task-reminders/", run_task_reminders),
    path("api/testing/send-email/", send_test_email),
    path("api/search/", SearchView.as_view(), name="search"),
    path("api/activity-feed/", ActivityFeedView.as_view(), name="activity-feed"),
    path("api/activity/", ActivityFeedView.as_view(), name="activity-legacy"),
    path("api/team-points/", TeamPointsView.as_view(), name="team-points"),
    path("api/analytics/artists/", ArtistEngagementView.as_view(), name="artist-engagement"),
    path("api/calendar/export/", calendar_export, name="calendar-export"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

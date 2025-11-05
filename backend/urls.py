from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import (
    register, stats,
    ProfileViewSet, RoleViewSet, ExampleViewSet, RequestViewSet,
    ChatThreadViewSet, ChatMessageViewSet, ProjectViewSet, TaskViewSet,
    ContractViewSet, PaymentViewSet, ReleaseViewSet, EventViewSet, BookingViewSet,
)

router = routers.DefaultRouter()
router.register(r"roles", RoleViewSet)
router.register(r"profiles", ProfileViewSet)
router.register(r"examples", ExampleViewSet)
router.register(r"requests", RequestViewSet)
router.register(r"threads", ChatThreadViewSet)
router.register(r"messages", ChatMessageViewSet)
router.register(r"projects", ProjectViewSet)
router.register(r"tasks", TaskViewSet)
router.register(r"contracts", ContractViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"releases", ReleaseViewSet)
router.register(r"events", EventViewSet)
router.register(r"bookings", BookingViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/register/", register),
    path("api/stats/", stats),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

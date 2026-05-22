from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PlayerViewSet, PlayerCoachViewSet, AttendanceStreakViewSet,
    CancellationRequestViewSet, LoyaltyPointsViewSet, ReferralCodeViewSet,
    CustomerScheduleView, CustomerDashboardView,
)

router = DefaultRouter()
# Register sub-paths FIRST so they don't get caught by the player detail pattern
router.register("coach-links", PlayerCoachViewSet, basename="player-coach")
router.register("streaks", AttendanceStreakViewSet, basename="attendance-streak")
router.register("cancellation-requests", CancellationRequestViewSet, basename="cancellation-request")
router.register("loyalty-points", LoyaltyPointsViewSet, basename="loyalty-points")
router.register("referral-codes", ReferralCodeViewSet, basename="referral-code")
# Register the catch-all player viewset LAST
router.register("", PlayerViewSet, basename="player")

urlpatterns = [
    path("my-schedule/", CustomerScheduleView.as_view(), name="my-schedule"),
    path("my-dashboard/", CustomerDashboardView.as_view(), name="my-dashboard"),
    path("", include(router.urls)),
]

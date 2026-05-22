from rest_framework.routers import DefaultRouter
from .views import GroupViewSet, GroupMembershipViewSet

router = DefaultRouter()
router.register("memberships", GroupMembershipViewSet, basename="membership")
router.register("", GroupViewSet, basename="group")
urlpatterns = router.urls

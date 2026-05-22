from rest_framework.routers import DefaultRouter
from .views import CoachViewSet

router = DefaultRouter()
router.register("", CoachViewSet, basename="coach")
urlpatterns = router.urls

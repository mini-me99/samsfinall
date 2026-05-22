from rest_framework.routers import DefaultRouter
from .views import AcademyViewSet

router = DefaultRouter()
router.register("", AcademyViewSet, basename="academy")

urlpatterns = router.urls

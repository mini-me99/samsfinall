from rest_framework.routers import DefaultRouter
from .views import VenueViewSet, SeriesViewSet, OccurrenceViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register("venues", VenueViewSet, basename="venue")
router.register("series", SeriesViewSet, basename="series")
router.register("occurrences", OccurrenceViewSet, basename="occurrence")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
urlpatterns = router.urls

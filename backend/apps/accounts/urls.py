from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MeView, UserViewSet, PublicUserListAPIView

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("users/search/", PublicUserListAPIView.as_view(), name="user-search"),
    path("", include(router.urls)),
]

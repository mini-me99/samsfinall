from rest_framework.viewsets import ModelViewSet
from .permissions import IsSameAcademy, HasRole


class AcademyMixin:
    """Resolves academy_id from the authenticated user after DRF auth."""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if user and user.is_authenticated and getattr(user, "academy_id", None):
            request.academy_id = user.academy_id
        else:
            request.academy_id = None


class AcademyScopedViewSet(AcademyMixin, ModelViewSet):
    """Base viewset that auto-filters and auto-stamps the academy."""

    permission_classes = [*ModelViewSet.permission_classes, IsSameAcademy, HasRole]
    allowed_roles = None

    def get_queryset(self):
        qs = super().get_queryset()
        academy_id = getattr(self.request, "academy_id", None)
        if academy_id is None:
            return qs.none()
        return qs.filter(academy_id=academy_id, deleted_at__isnull=True)

    def perform_create(self, serializer):
        serializer.save(academy_id=self.request.academy_id)

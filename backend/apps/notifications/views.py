from apps.common.viewsets import AcademyScopedViewSet
from apps.common.serializers import make_serializer
from .models import Notification

NotificationSerializer = make_serializer(Notification)


class NotificationViewSet(AcademyScopedViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()
    filterset_fields = ["status", "channel", "recipient"]
    ordering_fields = ["created_at"]
    allowed_roles = ["admin", "super_admin", "operations", "coach", "customer"]

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Academy
from .serializers import AcademySerializer


class AcademyViewSet(ReadOnlyModelViewSet):
    """Tenants only ever see their own academy record."""
    serializer_class = AcademySerializer

    def get_queryset(self):
        academy_id = getattr(self.request, "academy_id", None)
        if not academy_id:
            return Academy.objects.none()
        return Academy.objects.filter(id=academy_id)

    @action(detail=False, methods=["get"])
    def me(self, request):
        if not request.academy_id:
            return Response({"detail": "No tenant context"}, status=400)
        academy = Academy.objects.filter(id=request.academy_id).first()
        if not academy:
            return Response({"detail": "Not found"}, status=404)
        return Response(AcademySerializer(academy).data)

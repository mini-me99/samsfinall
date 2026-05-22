from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.viewsets import AcademyScopedViewSet
from apps.common.serializers import make_serializer
from apps.players.models import AttendanceStreak, Player
from .models import AttendanceRecord

AttendanceSerializer = make_serializer(AttendanceRecord)


def _update_streak(player, aid, attended):
    """Update attendance streak for a player."""
    streak, _ = AttendanceStreak.objects.get_or_create(
        player=player, academy_id=aid,
    )
    now = timezone.now()
    if attended:
        if streak.last_attended_at and (now - streak.last_attended_at).days <= 1:
            streak.current_streak += 1
        else:
            streak.current_streak = 1
        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_attended_at = now
        if not streak.streak_started_at:
            streak.streak_started_at = now
    else:
        streak.current_streak = 0
    streak.save()


class AttendanceViewSet(AcademyScopedViewSet):
    serializer_class = AttendanceSerializer
    queryset = AttendanceRecord.objects.all()
    filterset_fields = ["occurrence", "player", "status"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

    def perform_create(self, serializer):
        serializer.save(academy_id=self.request.academy_id, marked_by=self.request.user)

    @action(detail=False, methods=["post"])
    def bulk_mark(self, request):
        """Mark several players for one occurrence at once."""
        occurrence_id = request.data.get("occurrence")
        items = request.data.get("items", [])  # [{player, status, notes?}]
        if not occurrence_id:
            return Response({"detail": "occurrence required"}, status=400)
        out = []
        for it in items:
            obj, _ = AttendanceRecord.objects.update_or_create(
                academy_id=request.academy_id,
                occurrence_id=occurrence_id,
                player_id=it["player"],
                defaults=dict(
                    status=it.get("status", "present"),
                    notes=it.get("notes", ""),
                    marked_by=request.user,
                ),
            )
            out.append(str(obj.id))
            # Update streak
            attended = it.get("status") in ("present", "late")
            player = Player.objects.filter(id=it["player"], academy_id=request.academy_id).first()
            if player:
                _update_streak(player, request.academy_id, attended)
        return Response({"marked": len(out)}, status=status.HTTP_200_OK)

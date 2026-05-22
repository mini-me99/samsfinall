from django.utils import timezone
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum

from apps.common.viewsets import AcademyMixin
from apps.players.models import Player
from apps.sessions.models import SessionOccurrence
from apps.attendance.models import AttendanceRecord
from apps.payments.models import Invoice, Payment


class DashboardView(AcademyMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        aid = request.academy_id
        if not aid:
            return Response({"detail": "no tenant"}, status=400)

        role = getattr(request.user, "role", None)
        now = timezone.now()
        week_start = now - timedelta(days=now.weekday())

        result = {}

        if role in ("admin", "super_admin", "operations", "coach"):
            sessions_week = SessionOccurrence.objects.filter(
                academy_id=aid, starts_at__gte=week_start, deleted_at__isnull=True
            ).count()
            result["sessions_this_week"] = sessions_week

        if role in ("admin", "super_admin", "operations", "coach"):
            att_qs = AttendanceRecord.objects.filter(academy_id=aid, deleted_at__isnull=True)
            att_total = att_qs.count()
            att_present = att_qs.filter(status__in=["present", "late"]).count()
            result["attendance_rate"] = round((att_present / att_total) * 100, 1) if att_total else 0.0

        if role in ("admin", "super_admin", "operations", "coach"):
            active_players = Player.objects.filter(academy_id=aid, status="active", deleted_at__isnull=True).count()
            result["active_players"] = active_players

        if role in ("admin", "super_admin", "operations"):
            outstanding = Invoice.objects.filter(
                academy_id=aid, status__in=["issued", "overdue"], deleted_at__isnull=True
            ).aggregate(s=Sum("total"))["s"] or 0
            result["outstanding_amount"] = float(outstanding)

        if role in ("admin", "super_admin"):
            revenue_30 = Payment.objects.filter(
                academy_id=aid, received_at__gte=now - timedelta(days=30), deleted_at__isnull=True
            ).aggregate(s=Sum("amount"))["s"] or 0
            result["revenue_last_30_days"] = float(revenue_30)

        return Response(result)

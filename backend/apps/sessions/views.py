from datetime import timedelta, datetime
import zoneinfo
from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.viewsets import AcademyScopedViewSet
from apps.common.serializers import make_serializer
from .models import SessionSeries, SessionOccurrence, SessionEnrollment, Venue

VenueSerializer = make_serializer(Venue)
SeriesSerializer = make_serializer(SessionSeries)
EnrollmentSerializer = make_serializer(SessionEnrollment)


class OccurrenceSerializer(serializers.ModelSerializer):
    coaches = serializers.SerializerMethodField()
    coaches_ids = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = SessionOccurrence
        fields = ["id", "series", "title", "group", "venue", "coaches", "coaches_ids",
                  "starts_at", "ends_at", "capacity", "status", "notes",
                  "academy", "created_at", "updated_at"]
        read_only_fields = ["id", "academy", "created_at", "updated_at"]

    def get_coaches(self, obj):
        return [str(c.id) for c in obj.coaches.all()]

    def _localize(self, dt, academy_id):
        """Convert naive datetime from frontend (Cairo local) to aware datetime."""
        if dt is None or timezone.is_aware(dt):
            return dt
        tz = zoneinfo.ZoneInfo("Africa/Cairo")
        return timezone.make_aware(dt, tz)

    def create(self, validated_data):
        coaches_ids = validated_data.pop("coaches_ids", None) or validated_data.pop("coaches", None)
        # Localize naive datetimes from frontend
        academy_id = validated_data.get("academy_id")
        if "starts_at" in validated_data:
            validated_data["starts_at"] = self._localize(validated_data["starts_at"], academy_id)
        if "ends_at" in validated_data:
            validated_data["ends_at"] = self._localize(validated_data["ends_at"], academy_id)
        occurrence = SessionOccurrence.objects.create(**validated_data)
        if coaches_ids:
            occurrence.coaches.set(coaches_ids)
        return occurrence

    def update(self, instance, validated_data):
        coaches_ids = validated_data.pop("coaches_ids", None) or validated_data.pop("coaches", None)
        academy_id = validated_data.get("academy_id") or instance.academy_id
        if "starts_at" in validated_data:
            validated_data["starts_at"] = self._localize(validated_data["starts_at"], academy_id)
        if "ends_at" in validated_data:
            validated_data["ends_at"] = self._localize(validated_data["ends_at"], academy_id)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if coaches_ids is not None:
            instance.coaches.set(coaches_ids)
        instance.save()
        return instance


class VenueViewSet(AcademyScopedViewSet):
    serializer_class = VenueSerializer
    queryset = Venue.objects.all()
    search_fields = ["name", "address"]
    allowed_roles = ["admin", "super_admin", "operations"]

class SeriesViewSet(AcademyScopedViewSet):
    serializer_class = SeriesSerializer
    queryset = SessionSeries.objects.all()
    search_fields = ["title"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        """Generate concrete occurrences from this series within the given window."""
        series = self.get_object()
        start = request.data.get("start_date")
        end = request.data.get("end_date")
        if not start or not end:
            return Response({"detail": "start_date and end_date required"}, status=400)
        d0 = datetime.fromisoformat(start).date()
        d1 = datetime.fromisoformat(end).date()
        created = []
        cur = max(series.start_date, d0)
        limit = min(series.end_date or d1, d1)
        while cur <= limit:
            include = False
            if series.recurrence == SessionSeries.Recurrence.ONCE:
                include = cur == series.start_date
            elif series.recurrence == SessionSeries.Recurrence.DAILY:
                include = True
            elif series.recurrence == SessionSeries.Recurrence.WEEKLY:
                bit = 1 << cur.weekday()
                include = bool(series.weekly_mask & bit)
            if include:
                starts = datetime.combine(cur, series.start_time)
                ends = datetime.combine(cur, series.end_time)
                occ, made = SessionOccurrence.objects.get_or_create(
                    academy_id=series.academy_id,
                    series=series,
                    starts_at=starts,
                    defaults=dict(
                        title=series.title, group=series.group, venue=series.venue,
                        ends_at=ends, capacity=series.capacity,
                    ),
                )
                if made:
                    created.append(occ.id)
            cur += timedelta(days=1)
            if series.recurrence == SessionSeries.Recurrence.ONCE:
                break
        return Response({"created": len(created)}, status=201)


class OccurrenceViewSet(AcademyScopedViewSet):
    serializer_class = OccurrenceSerializer
    queryset = SessionOccurrence.objects.all()
    filterset_fields = ["status", "group", "venue"]
    ordering_fields = ["starts_at"]
    search_fields = ["title"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

    def get_queryset(self):
        qs = super().get_queryset()
        coach_id = self.request.query_params.get("coaches")
        if coach_id:
            qs = qs.filter(coaches__id=coach_id)
        return qs

class EnrollmentViewSet(AcademyScopedViewSet):
    serializer_class = EnrollmentSerializer
    queryset = SessionEnrollment.objects.all()
    filterset_fields = ["occurrence", "player"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

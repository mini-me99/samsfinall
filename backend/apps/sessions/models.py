from django.db import models
from apps.common.models import AcademyScopedModel


class SessionSeries(AcademyScopedModel):
    """A recurring session template. Concrete occurrences are generated from it."""

    class Recurrence(models.TextChoices):
        ONCE = "once", "Once"
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    title = models.CharField(max_length=160)
    group = models.ForeignKey("groups.Group", null=True, blank=True, on_delete=models.SET_NULL, related_name="series")
    venue = models.ForeignKey("training.Venue", null=True, blank=True, on_delete=models.SET_NULL, related_name="series")
    coaches = models.ManyToManyField("coaches.Coach", blank=True, related_name="series")
    recurrence = models.CharField(max_length=10, choices=Recurrence.choices, default=Recurrence.WEEKLY)
    # bitmask Mon=1..Sun=64 for weekly recurrence
    weekly_mask = models.PositiveSmallIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Venue(AcademyScopedModel):
    """Re-export to keep `apps.sessions.Venue` namespace usable by SessionSeries FK."""
    # NB: actual Venue lives in groups app via M2M but here we keep a simple registry.
    name = models.CharField(max_length=160)
    address = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class SessionOccurrence(AcademyScopedModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    series = models.ForeignKey(SessionSeries, null=True, blank=True, on_delete=models.SET_NULL, related_name="occurrences")
    title = models.CharField(max_length=160)
    group = models.ForeignKey("groups.Group", null=True, blank=True, on_delete=models.SET_NULL, related_name="occurrences")
    venue = models.ForeignKey(Venue, null=True, blank=True, on_delete=models.SET_NULL, related_name="occurrences")
    coaches = models.ManyToManyField("coaches.Coach", blank=True, related_name="occurrences")
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)

    class Meta(AcademyScopedModel.Meta):
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "starts_at"]),
            models.Index(fields=["academy", "status"]),
        ]
        ordering = ["starts_at"]

    def __str__(self):
        return f"{self.title} @ {self.starts_at:%Y-%m-%d %H:%M}"


class SessionEnrollment(AcademyScopedModel):
    occurrence = models.ForeignKey(SessionOccurrence, on_delete=models.CASCADE, related_name="enrollments")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="enrollments")

    class Meta(AcademyScopedModel.Meta):
        constraints = [models.UniqueConstraint(fields=["occurrence", "player"], name="uniq_occurrence_player")]

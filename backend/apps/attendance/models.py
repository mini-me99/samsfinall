from django.db import models
from apps.common.models import AcademyScopedModel


class AttendanceRecord(AcademyScopedModel):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    occurrence = models.ForeignKey("training.SessionOccurrence", on_delete=models.CASCADE, related_name="attendance")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="attendance")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    marked_at = models.DateTimeField(auto_now=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta(AcademyScopedModel.Meta):
        constraints = [models.UniqueConstraint(fields=["occurrence", "player"], name="uniq_attendance_per_session")]
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "status"]),
        ]

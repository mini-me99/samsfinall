from django.db import models
from apps.common.models import AcademyScopedModel


class Coach(AcademyScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    specialty = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="coach_profiles")

    class Meta(AcademyScopedModel.Meta):
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "status"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

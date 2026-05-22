from django.db import models
from apps.common.models import AcademyScopedModel


class Notification(AcademyScopedModel):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "In-app"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        READ = "read", "Read"

    recipient = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="notifications")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)

    class Meta(AcademyScopedModel.Meta):
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "status"]),
        ]

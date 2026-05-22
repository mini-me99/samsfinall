import uuid
from django.db import models


class SubscriptionPlan(models.TextChoices):
    TRIAL = "trial", "Trial"
    BASIC = "basic", "Basic"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class AcademyStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SUSPENDED = "suspended", "Suspended"
    ARCHIVED = "archived", "Archived"


class Academy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    subscription_plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.TRIAL)
    status = models.CharField(max_length=20, choices=AcademyStatus.choices, default=AcademyStatus.ACTIVE)
    branding_settings = models.JSONField(default=dict, blank=True)
    timezone = models.CharField(max_length=64, default="Africa/Cairo")
    language = models.CharField(max_length=8, default="en")
    currency = models.CharField(max_length=8, default="EGP")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

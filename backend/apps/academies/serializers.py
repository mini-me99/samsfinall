from rest_framework import serializers
from .models import Academy


class AcademySerializer(serializers.ModelSerializer):
    class Meta:
        model = Academy
        fields = ["id", "name", "slug", "subscription_plan", "status",
                  "branding_settings", "timezone", "language", "currency",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

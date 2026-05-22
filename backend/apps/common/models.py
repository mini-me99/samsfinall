import uuid
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)


class TimeStampedModel(models.Model):
    """UUID PK + created_at/updated_at + soft delete."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self):
        super().delete()


class AcademyScopedQuerySet(SoftDeleteQuerySet):
    def for_academy(self, academy_id):
        return self.filter(academy_id=academy_id)


class AcademyScopedModel(TimeStampedModel):
    """Every operational entity inherits from this for multi-tenant isolation."""

    academy = models.ForeignKey(
        "academies.Academy",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s_set",
        db_index=True,
    )

    objects = AcademyScopedQuerySet.as_manager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["academy", "created_at"]),
        ]

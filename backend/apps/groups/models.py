from django.db import models
from apps.common.models import AcademyScopedModel


class Venue(AcademyScopedModel):
    name = models.CharField(max_length=160)
    address = models.CharField(max_length=255, blank=True)
    capacity = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Group(AcademyScopedModel):
    name = models.CharField(max_length=160)
    age_min = models.PositiveSmallIntegerField(default=0)
    age_max = models.PositiveSmallIntegerField(default=99)
    capacity = models.PositiveIntegerField(default=20)
    primary_coach = models.ForeignKey("coaches.Coach", null=True, blank=True, on_delete=models.SET_NULL, related_name="primary_groups")
    members = models.ManyToManyField("players.Player", through="GroupMembership", related_name="groups")

    def __str__(self):
        return self.name


class GroupMembership(AcademyScopedModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    player = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="group_memberships")
    joined_at = models.DateField(auto_now_add=True)

    class Meta(AcademyScopedModel.Meta):
        constraints = [models.UniqueConstraint(fields=["group", "player"], name="uniq_group_player")]

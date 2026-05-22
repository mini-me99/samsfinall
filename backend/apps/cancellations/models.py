from django.db import models
from apps.common.models import AcademyScopedModel


class CancellationRequest(AcademyScopedModel):
    """A request to cancel a session occurrence."""
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        GROUP_VOTING = "group_voting", "Group Voting"
        GROUP_APPROVED = "group_approved", "Group Approved"
        COACH_REVIEW = "coach_review", "Coach Review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    occurrence = models.ForeignKey("training.SessionOccurrence", on_delete=models.CASCADE, related_name="cancellation_requests")
    requester = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="cancellation_requests")
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey("coaches.Coach", null=True, blank=True, on_delete=models.SET_NULL, related_name="cancellation_reviews")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    coach_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(AcademyScopedModel.Meta):
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cancel {self.occurrence} by {self.requester}"


class CancellationVote(AcademyScopedModel):
    """Vote by a group member on a cancellation request."""
    request = models.ForeignKey(CancellationRequest, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey("players.Player", on_delete=models.CASCADE, related_name="cancellation_votes")
    approved = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta(AcademyScopedModel.Meta):
        constraints = [models.UniqueConstraint(fields=["request", "voter"], name="uniq_vote_per_player")]

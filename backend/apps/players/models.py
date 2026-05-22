import uuid
from django.db import models
from apps.common.models import AcademyScopedModel


class Player(AcademyScopedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ARCHIVED = "archived", "Archived"

    class Preference(models.TextChoices):
        ALONE = "alone", "Alone"
        PARTNER = "partner", "With Partner"
        GROUP = "group", "In a Group"

    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    guardian_name = models.CharField(max_length=160, blank=True)
    guardian_phone = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    notes = models.TextField(blank=True)
    user = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="player_profiles")

    # New preference fields
    preference_type = models.CharField(max_length=10, choices=Preference.choices, default=Preference.ALONE)
    preferred_days = models.JSONField(default=list, blank=True, help_text="e.g. ['sunday','wednesday']")
    preferred_time = models.TimeField(null=True, blank=True, help_text="Preferred session time")
    linked_partner = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="partner_of")

    class Meta(AcademyScopedModel.Meta):
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "status"]),
            models.Index(fields=["academy", "last_name"]),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PlayerCoach(AcademyScopedModel):
    """Links a player to a coach. Operations assign players to coaches."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="coach_links")
    coach = models.ForeignKey("coaches.Coach", on_delete=models.CASCADE, related_name="player_links")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta(AcademyScopedModel.Meta):
        constraints = [models.UniqueConstraint(fields=["player", "coach"], name="uniq_player_coach")]


class AttendanceStreak(AcademyScopedModel):
    """Tracks consecutive attendance without cancellation."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="streaks")
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_attended_at = models.DateTimeField(null=True, blank=True)
    streak_started_at = models.DateTimeField(null=True, blank=True)
    share_token = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)

    class Meta(AcademyScopedModel.Meta):
        verbose_name_plural = "Attendance streaks"

    def __str__(self):
        return f"{self.player} — {self.current_streak} day streak"


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
    requester = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="cancellation_requests")
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
    voter = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="cancellation_votes")
    approved = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta(AcademyScopedModel.Meta):
        constraints = [models.UniqueConstraint(fields=["request", "voter"], name="uniq_vote_per_player")]


class LoyaltyPoints(AcademyScopedModel):
    """Loyalty points awarded by operations."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="loyalty_points")
    points = models.IntegerField(default=0)
    reason = models.CharField(max_length=255)
    awarded_by = models.ForeignKey("accounts.User", null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(AcademyScopedModel.Meta):
        verbose_name_plural = "Loyalty points"
        ordering = ["-created_at"]


class ReferralCode(AcademyScopedModel):
    """Referral code for each customer user."""
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="referral_codes")
    code = models.CharField(max_length=20, unique=True)
    referred_by = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="referrals")
    points_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} — {self.code}"

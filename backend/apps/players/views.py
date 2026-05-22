from django.utils import timezone
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum
from apps.common.viewsets import AcademyScopedViewSet, AcademyMixin
from apps.common.serializers import make_serializer
from apps.sessions.models import SessionEnrollment, SessionOccurrence
from apps.notifications.models import Notification
from apps.cancellations.models import CancellationRequest, CancellationVote
from .models import Player, PlayerCoach, AttendanceStreak, LoyaltyPoints, ReferralCode


PlayerSerializer = make_serializer(Player)


class PlayerCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)

    class Meta:
        model = Player
        fields = "__all__"
        read_only_fields = ["id", "academy", "created_at", "updated_at", "user"]

    def create(self, validated_data):
        from apps.accounts.models import User, UserRole
        from apps.players.models import ReferralCode
        import secrets
        password = validated_data.pop("password", None)
        player = Player.objects.create(**validated_data)
        if password:
            email = player.email or f"{player.first_name.lower()}.{player.last_name.lower()}@sams.local"
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "role": UserRole.CUSTOMER,
                    "first_name": player.first_name,
                    "last_name": player.last_name,
                    "phone": player.phone,
                    "academy_id": player.academy_id,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(password)
                user.save()
                player.user = user
                player.save(update_fields=["user"])
                # Auto-create referral code
                code = secrets.token_hex(4).upper()
                ReferralCode.objects.create(user=user, code=code, academy_id=player.academy_id)
        return player


class PlayerUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)

    class Meta:
        model = Player
        fields = "__all__"
        read_only_fields = ["id", "academy", "created_at", "updated_at", "user"]

    def update(self, instance, validated_data):
        from apps.accounts.models import User, UserRole
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            email = instance.email or f"{instance.first_name.lower()}.{instance.last_name.lower()}@sams.local"
            if instance.user:
                instance.user.set_password(password)
                instance.user.save()
            else:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        "role": UserRole.CUSTOMER,
                        "first_name": instance.first_name,
                        "last_name": instance.last_name,
                        "phone": instance.phone,
                        "academy_id": instance.academy_id,
                        "is_active": True,
                    },
                )
                if created:
                    user.set_password(password)
                    user.save()
                    instance.user = user
        instance.save()
        return instance


class PlayerViewSet(AcademyScopedViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.all()
    search_fields = ["first_name", "last_name", "email", "phone", "guardian_name"]
    filterset_fields = ["status", "gender", "preference_type"]
    ordering_fields = ["last_name", "created_at"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

    def get_serializer_class(self):
        if self.action == "create":
            return PlayerCreateSerializer
        if self.action in ("update", "partial_update"):
            return PlayerUpdateSerializer
        return PlayerSerializer

    def perform_create(self, serializer):
        serializer.save(academy_id=self.request.academy_id)


class PlayerCoachViewSet(AcademyScopedViewSet):
    """Links players to coaches."""
    serializer_class = make_serializer(PlayerCoach)
    queryset = PlayerCoach.objects.all()
    filterset_fields = ["player", "coach"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]


class AttendanceStreakViewSet(AcademyScopedViewSet):
    """View and manage attendance streaks."""
    serializer_class = make_serializer(AttendanceStreak)
    queryset = AttendanceStreak.objects.all()
    filterset_fields = ["player"]
    allowed_roles = ["admin", "super_admin", "operations", "coach", "customer"]


class CancellationRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.SerializerMethodField()
    occurrence_title = serializers.SerializerMethodField()
    occurrence_time = serializers.SerializerMethodField()

    class Meta:
        model = CancellationRequest
        fields = ["id", "occurrence", "requester", "requester_name",
                  "occurrence_title", "occurrence_time", "reason", "status",
                  "reviewed_by", "reviewed_at", "coach_notes", "created_at",
                  "academy"]
        read_only_fields = ["id", "requester", "requester_name",
                           "occurrence_title", "occurrence_time",
                           "status", "reviewed_by",
                           "reviewed_at", "coach_notes", "created_at", "academy"]

    def get_requester_name(self, obj):
        return f"{obj.requester.first_name} {obj.requester.last_name}" if obj.requester else "—"

    def get_occurrence_title(self, obj):
        return obj.occurrence.title if obj.occurrence else "—"

    def get_occurrence_time(self, obj):
        if obj.occurrence:
            return obj.occurrence.starts_at.strftime("%Y-%m-%d %H:%M")
        return "—"


class CancellationRequestViewSet(AcademyScopedViewSet):
    """Customer cancellation requests with group voting."""
    serializer_class = CancellationRequestSerializer
    queryset = CancellationRequest.objects.all()
    filterset_fields = ["status", "occurrence", "requester"]
    allowed_roles = ["admin", "super_admin", "operations", "coach", "customer"]

    def get_queryset(self):
        qs = super().get_queryset()
        coach_id = self.request.query_params.get("coach")
        if coach_id:
            qs = qs.filter(occurrence__coaches__id=coach_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        player = Player.objects.filter(user=user, academy_id=self.request.academy_id).first()
        if not player:
            raise serializers.ValidationError({"detail": "No player profile linked to your account"})
        req = serializer.save(academy_id=self.request.academy_id, requester=player)
        occurrence = req.occurrence
        # If the occurrence is linked to a group, start group voting
        if occurrence.group:
            members = occurrence.group.members.all()
            if members.count() > 1:
                req.status = CancellationRequest.Status.GROUP_VOTING
                req.save(update_fields=["status"])
                # Notify all group members
                for player in members:
                    if player.user:
                        Notification.objects.create(
                            academy_id=self.request.academy_id,
                            recipient=player.user,
                            title="Cancellation Vote Required",
                            body=f"{req.requester.first_name} requested to cancel {occurrence.title}. Please vote.",
                            channel="in_app",
                        )
            else:
                req.status = CancellationRequest.Status.COACH_REVIEW
                req.save(update_fields=["status"])
                # Notify coach
                if occurrence.coaches.exists():
                    for coach in occurrence.coaches.all():
                        if coach.user:
                            Notification.objects.create(
                                academy_id=self.request.academy_id,
                                recipient=coach.user,
                                title="Cancellation Request",
                                body=f"{req.requester.first_name} wants to cancel {occurrence.title}.",
                                channel="in_app",
                            )
        else:
            req.status = CancellationRequest.Status.COACH_REVIEW
            req.save(update_fields=["status"])
            if occurrence.coaches.exists():
                for coach in occurrence.coaches.all():
                    if coach.user:
                        Notification.objects.create(
                            academy_id=self.request.academy_id,
                            recipient=coach.user,
                            title="Cancellation Request",
                            body=f"{req.requester.first_name} wants to cancel {occurrence.title}.",
                            channel="in_app",
                        )

    @action(detail=True, methods=["post"])
    def vote(self, request, pk=None):
        """Group member votes on a cancellation request."""
        req = self.get_object()
        voter_id = request.data.get("voter_id")
        approved = request.data.get("approved", True)
        if not voter_id:
            return Response({"detail": "voter_id required"}, status=400)
        vote, _ = CancellationVote.objects.update_or_create(
            academy_id=request.academy_id,
            request=req,
            voter_id=voter_id,
            defaults={"approved": approved},
        )
        # Check if all group members have voted
        all_players = req.occurrence.group.members.all()
        votes = req.votes.all()
        voted_ids = set(str(v.voter_id) for v in votes)
        all_ids = set(str(p.id) for p in all_players)
        if voted_ids == all_ids:
            all_approved = all(v.approved for v in votes)
            if all_approved:
                req.status = CancellationRequest.Status.COACH_REVIEW
                req.save(update_fields=["status"])
                # Notify coaches
                for coach in req.occurrence.coaches.all():
                    if coach.user:
                        Notification.objects.create(
                            academy_id=self.request.academy_id,
                            recipient=coach.user,
                            title="Group Approved Cancellation",
                            body=f"All group members approved cancelling {req.occurrence.title}. Please review.",
                            channel="in_app",
                        )
            else:
                req.status = CancellationRequest.Status.REJECTED
                req.save(update_fields=["status"])
                Notification.objects.create(
                    academy_id=self.request.academy_id,
                    recipient=req.requester.user,
                    title="Cancellation Rejected",
                    body=f"Your group did not approve cancelling {req.occurrence.title}.",
                    channel="in_app",
                )
        return Response({"status": req.status})

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """Coach approves or rejects a cancellation request."""
        req = self.get_object()
        action_val = request.data.get("action")
        coach_id = request.data.get("coach_id")
        notes = request.data.get("notes", "")
        if action_val not in ("approve", "reject"):
            return Response({"detail": "action must be 'approve' or 'reject'"}, status=400)
        req.reviewed_by_id = coach_id
        req.reviewed_at = timezone.now()
        req.coach_notes = notes
        if action_val == "approve":
            req.status = CancellationRequest.Status.APPROVED
            req.occurrence.status = SessionOccurrence.Status.CANCELLED
            req.occurrence.save(update_fields=["status"])
        else:
            req.status = CancellationRequest.Status.REJECTED
        req.save()
        # Notify requester
        if req.requester.user:
            status_text = "approved" if action_val == "approve" else "rejected"
            Notification.objects.create(
                academy_id=self.request.academy_id,
                recipient=req.requester.user,
                title=f"Cancellation {status_text}",
                body=f"Your request to cancel {req.occurrence.title} was {status_text}.",
                channel="in_app",
            )
        # Notify group members
        if req.occurrence.group:
            for player in req.occurrence.group.members.all():
                if player.user and player.id != req.requester.id:
                    Notification.objects.create(
                        academy_id=self.request.academy_id,
                        recipient=player.user,
                        title=f"Cancellation {status_text}",
                        body=f"The session {req.occurrence.title} was {status_text}.",
                        channel="in_app",
                    )
        return Response({"status": req.status})


class LoyaltyPointsViewSet(AcademyScopedViewSet):
    """Operations-managed loyalty points."""
    serializer_class = make_serializer(LoyaltyPoints)
    queryset = LoyaltyPoints.objects.all()
    filterset_fields = ["player"]
    ordering_fields = ["-created_at"]
    allowed_roles = ["admin", "super_admin", "operations"]

    def perform_create(self, serializer):
        serializer.save(academy_id=self.request.academy_id, awarded_by=self.request.user)


class ReferralCodeViewSet(AcademyScopedViewSet):
    """Referral codes for customers."""
    serializer_class = make_serializer(ReferralCode)
    queryset = ReferralCode.objects.all()
    filterset_fields = ["user"]
    search_fields = ["code"]
    allowed_roles = ["admin", "super_admin", "operations", "customer"]

    @action(detail=True, methods=["post"])
    def award_points(self, request, pk=None):
        """Operations awards points for a referral."""
        ref = self.get_object()
        points = request.data.get("points", 10)
        ref.points_awarded += int(points)
        ref.save(update_fields=["points_awarded"])
        if ref.user:
            Notification.objects.create(
                academy_id=self.request.academy_id,
                recipient=ref.user,
                title="Referral Points Awarded",
                body=f"You received {points} loyalty points for your referral!",
                channel="in_app",
            )
        return Response({"points_awarded": ref.points_awarded})


class CustomerScheduleView(AcademyMixin, APIView):
    """Returns the schedule for the current customer user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "customer":
            return Response({"detail": "Only for customers"}, status=403)
        player = Player.objects.filter(user=user, academy_id=request.academy_id).first()
        if not player:
            return Response({"detail": "No player profile"}, status=404)

        from_date = request.query_params.get("from")
        to_date = request.query_params.get("to")
        enrollments = SessionEnrollment.objects.filter(
            player=player, academy_id=request.academy_id,
            occurrence__deleted_at__isnull=True,
        ).select_related("occurrence", "occurrence__venue", "occurrence__group")
        if from_date:
            enrollments = enrollments.filter(occurrence__starts_at__gte=from_date)
        if to_date:
            enrollments = enrollments.filter(occurrence__starts_at__lte=to_date)

        schedule = []
        for e in enrollments:
            occ = e.occurrence
            schedule.append({
                "id": str(occ.id),
                "title": occ.title,
                "starts_at": occ.starts_at.isoformat(),
                "ends_at": occ.ends_at.isoformat(),
                "venue": occ.venue.name if occ.venue else None,
                "group": occ.group.name if occ.group else None,
                "status": occ.status,
                "enrolled": True,
            })
        return Response(schedule)


class CustomerDashboardView(AcademyMixin, APIView):
    """Customer-specific dashboard data."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "customer":
            return Response({"detail": "Only for customers"}, status=403)
        player = Player.objects.filter(user=user, academy_id=request.academy_id).first()
        if not player:
            return Response({"empty": True})

        aid = request.academy_id
        now = timezone.now()

        # Upcoming sessions
        upcoming = SessionEnrollment.objects.filter(
            player=player, academy_id=aid,
            occurrence__starts_at__gte=now,
            occurrence__deleted_at__isnull=True,
            occurrence__status=SessionOccurrence.Status.SCHEDULED,
        ).select_related("occurrence", "occurrence__venue").order_by("occurrence__starts_at")[:10]

        # Streak
        streak = AttendanceStreak.objects.filter(player=player, academy_id=aid).first()

        # Points
        total_points = LoyaltyPoints.objects.filter(player=player, academy_id=aid).aggregate(s=Sum("points"))["s"] or 0

        # Cancellation requests
        cancel_requests = CancellationRequest.objects.filter(requester=player, academy_id=aid).count()

        return Response({
            "upcoming_sessions": [
                {
                    "id": str(e.occurrence.id),
                    "title": e.occurrence.title,
                    "starts_at": e.occurrence.starts_at.isoformat(),
                    "venue": e.occurrence.venue.name if e.occurrence.venue else None,
                    "status": e.occurrence.status,
                }
                for e in upcoming
            ],
            "streak": {
                "current": streak.current_streak if streak else 0,
                "longest": streak.longest_streak if streak else 0,
            } if streak else {"current": 0, "longest": 0},
            "total_points": total_points,
            "pending_cancellations": cancel_requests,
        })

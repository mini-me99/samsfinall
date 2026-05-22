from rest_framework import serializers
from apps.common.viewsets import AcademyScopedViewSet
from apps.common.serializers import make_serializer
from apps.accounts.models import User, UserRole
from .models import Coach

CoachSerializer = make_serializer(Coach)


class CoachCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)

    class Meta:
        model = Coach
        fields = ["id", "first_name", "last_name", "email", "phone",
                  "specialty", "bio", "status", "password", "user"]
        read_only_fields = ["id", "user"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        coach = Coach.objects.create(**validated_data)
        if password and coach.email:
            user, created = User.objects.get_or_create(
                email=coach.email,
                defaults={
                    "role": UserRole.COACH,
                    "first_name": coach.first_name,
                    "last_name": coach.last_name,
                    "phone": coach.phone,
                    "academy_id": coach.academy_id,
                    "is_active": True,
                },
            )
            if created:
                user.set_password(password)
                user.save()
                coach.user = user
                coach.save(update_fields=["user"])
        return coach


class CoachUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4, required=False)

    class Meta:
        model = Coach
        fields = ["id", "first_name", "last_name", "email", "phone",
                  "specialty", "bio", "status", "password"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password and instance.email:
            if instance.user:
                instance.user.set_password(password)
                instance.user.save()
            else:
                user = User.objects.create_user(
                    email=instance.email,
                    password=password,
                    role=UserRole.COACH,
                    first_name=instance.first_name,
                    last_name=instance.last_name,
                    academy_id=instance.academy_id,
                )
                instance.user = user
        instance.save()
        return instance


class CoachViewSet(AcademyScopedViewSet):
    serializer_class = CoachSerializer
    queryset = Coach.objects.all()
    search_fields = ["first_name", "last_name", "email", "specialty"]
    filterset_fields = ["status", "user"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

    def get_serializer_class(self):
        if self.action == "create":
            return CoachCreateSerializer
        if self.action in ("update", "partial_update"):
            return CoachUpdateSerializer
        return CoachSerializer

    def perform_create(self, serializer):
        serializer.save(academy_id=self.request.academy_id)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["academy_id"] = getattr(self.request, "academy_id", None)
        return ctx

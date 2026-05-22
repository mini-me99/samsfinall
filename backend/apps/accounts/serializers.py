from rest_framework import serializers
from .models import User, UserRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone",
                  "role", "academy", "mfa_enabled", "is_active"]
        read_only_fields = ["id", "academy", "mfa_enabled"]


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ["id", "role", "academy", "mfa_enabled", "is_active"]


class AdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone",
                  "role", "password", "is_active"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        academy_id = self.context.get("academy_id")
        user = User(**validated_data, academy_id=academy_id)
        user.set_password(password)
        user.save()
        return user


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone",
                  "role", "password", "is_active"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

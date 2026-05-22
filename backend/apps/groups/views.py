from rest_framework import serializers
from apps.common.viewsets import AcademyScopedViewSet
from apps.common.serializers import make_serializer
from .models import Group, GroupMembership

GroupSerializer = make_serializer(Group)
GroupMembershipSerializer = make_serializer(GroupMembership)


class GroupViewSet(AcademyScopedViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()
    search_fields = ["name"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]


class GroupMembershipViewSet(AcademyScopedViewSet):
    serializer_class = GroupMembershipSerializer
    queryset = GroupMembership.objects.all()
    filterset_fields = ["group", "player"]
    allowed_roles = ["admin", "super_admin", "operations", "coach"]

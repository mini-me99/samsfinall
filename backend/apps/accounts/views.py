from django.db import models
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.common.viewsets import AcademyMixin
from .models import User, UserRole
from .serializers import (
    MeSerializer, UserSerializer,
    AdminUserCreateSerializer, AdminUserUpdateSerializer,
)


class MeView(APIView):
    def get(self, request):
        return Response(MeSerializer(request.user).data)


class PublicUserSearchView(AcademyMixin, APIView):
    """Searchable user list for operations/coach roles (read-only, no create/update)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role
        if role not in ("admin", "super_admin", "operations", "coach"):
            return Response({"detail": "Not allowed"}, status=403)
        aid = request.academy_id
        qs = User.objects.filter(academy_id=aid).order_by("-created_at")
        search = request.query_params.get("search", "")
        if search:
            qs = qs.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(phone__icontains=search)
            )
        role_filter = request.query_params.get("role", "")
        if role_filter:
            qs = qs.filter(role=role_filter)
        page_size = int(request.query_params.get("page_size", 200))
        from django.core.paginator import Paginator
        paginator = Paginator(qs, page_size)
        page = int(request.query_params.get("page", 1))
        items = paginator.get_page(page)
        return Response({
            "count": paginator.count,
            "results": UserSerializer(items, many=True).data,
        })


class IsAcademyAdmin(IsAuthenticated):
    """Only admins / super-admins can manage user accounts."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)


class UserViewSet(AcademyMixin, viewsets.ModelViewSet):
    """Admin-only CRUD over users within the same academy."""
    permission_classes = [IsAcademyAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["email", "first_name", "last_name", "phone"]
    filterset_fields = ["role", "is_active"]

    def get_queryset(self):
        academy_id = getattr(self.request, "academy_id", None)
        qs = User.objects.all().order_by("-created_at")
        if academy_id is not None:
            qs = qs.filter(academy_id=academy_id)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return AdminUserCreateSerializer
        if self.action in ("update", "partial_update"):
            return AdminUserUpdateSerializer
        return UserSerializer

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["academy_id"] = getattr(self.request, "academy_id", None)
        return ctx


class PublicUserListAPIView(AcademyMixin, APIView):
    """Read-only user list for operations/coach roles (searchable)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role
        if role not in ("admin", "super_admin", "operations", "coach"):
            return Response({"detail": "Not allowed"}, status=403)
        aid = request.academy_id
        qs = User.objects.filter(academy_id=aid).order_by("-created_at")
        search = request.query_params.get("search", "")
        if search:
            qs = qs.filter(
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search) |
                models.Q(phone__icontains=search)
            )
        role_filter = request.query_params.get("role", "")
        if role_filter:
            qs = qs.filter(role=role_filter)
        page_size = int(request.query_params.get("page_size", 200))
        from django.core.paginator import Paginator
        paginator = Paginator(qs, page_size)
        page = int(request.query_params.get("page", 1))
        items = paginator.get_page(page)
        return Response({
            "count": paginator.count,
            "results": [{"id": u.id, "email": u.email, "first_name": u.first_name, "last_name": u.last_name, "role": u.role} for u in items],
        })

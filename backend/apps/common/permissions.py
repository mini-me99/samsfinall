from rest_framework.permissions import BasePermission


class IsSameAcademy(BasePermission):
    """Object-level guard: object.academy_id must match request.academy_id."""

    def has_object_permission(self, request, view, obj):
        academy_id = getattr(request, "academy_id", None)
        return academy_id is not None and str(getattr(obj, "academy_id", None)) == str(academy_id)


class HasRole(BasePermission):
    """Allow users whose role is in view.allowed_roles."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        allowed = getattr(view, "allowed_roles", None)
        if not allowed:
            return True
        return request.user.role in allowed

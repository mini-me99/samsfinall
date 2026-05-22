"""Tenant middleware: resolves the active academy for each request."""
from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    """
    Resolves the current academy from the authenticated user and attaches it
    to the request as `request.academy_id`. View / queryset code MUST filter
    by this id — never trust client-supplied academy identifiers.
    """

    def process_request(self, request):
        request.academy_id = None
        user = getattr(request, "user", None)
        if user and user.is_authenticated and getattr(user, "academy_id", None):
            request.academy_id = user.academy_id
        return None

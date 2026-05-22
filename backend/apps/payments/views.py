from apps.common.viewsets import AcademyScopedViewSet
from apps.common.serializers import make_serializer
from .models import Invoice, InvoiceLine, Payment

InvoiceSerializer = make_serializer(Invoice)
InvoiceLineSerializer = make_serializer(InvoiceLine)
PaymentSerializer = make_serializer(Payment)


class InvoiceViewSet(AcademyScopedViewSet):
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
    filterset_fields = ["status", "player"]
    search_fields = ["number"]
    allowed_roles = ["admin", "super_admin", "operations"]

class InvoiceLineViewSet(AcademyScopedViewSet):
    serializer_class = InvoiceLineSerializer
    queryset = InvoiceLine.objects.all()
    filterset_fields = ["invoice"]
    allowed_roles = ["admin", "super_admin", "operations"]

class PaymentViewSet(AcademyScopedViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filterset_fields = ["method", "player", "invoice"]
    ordering_fields = ["received_at"]
    allowed_roles = ["admin", "super_admin", "operations"]

from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceLineViewSet, PaymentViewSet

router = DefaultRouter()
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("invoice-lines", InvoiceLineViewSet, basename="invoice-line")
router.register("payments", PaymentViewSet, basename="payment")
urlpatterns = router.urls

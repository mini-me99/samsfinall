from decimal import Decimal
from django.db import models
from apps.common.models import AcademyScopedModel


class Invoice(AcademyScopedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ISSUED = "issued", "Issued"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        CANCELLED = "cancelled", "Cancelled"

    number = models.CharField(max_length=40, blank=True)
    player = models.ForeignKey("players.Player", null=True, blank=True, on_delete=models.SET_NULL, related_name="invoices")
    issue_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    currency = models.CharField(max_length=8, default="EGP")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    notes = models.TextField(blank=True)

    class Meta(AcademyScopedModel.Meta):
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "status"]),
            models.Index(fields=["academy", "due_date"]),
        ]


class InvoiceLine(AcademyScopedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))


class Payment(AcademyScopedModel):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        TRANSFER = "transfer", "Transfer"
        ONLINE = "online", "Online"

    invoice = models.ForeignKey(Invoice, null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    player = models.ForeignKey("players.Player", null=True, blank=True, on_delete=models.SET_NULL, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="EGP")
    method = models.CharField(max_length=12, choices=Method.choices, default=Method.CASH)
    received_at = models.DateTimeField()
    reference = models.CharField(max_length=120, blank=True)
    notes = models.TextField(blank=True)

    class Meta(AcademyScopedModel.Meta):
        indexes = AcademyScopedModel.Meta.indexes + [
            models.Index(fields=["academy", "received_at"]),
        ]

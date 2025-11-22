from typing import override

from django.db import models

from api.data.customer_data import Customer
from api.data.product_data import Product
from api.data.pharmacy_data import Pharmacy


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending"
        RECEIVED = "Received"
        CANCELLED = "Cancelled"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    status = models.CharField(choices=Status, default=Status.PENDING)

    @override
    def __repr__(self) -> str:
        repr = f"{self.id} {self.customer} ({self.products.all()})"
        return repr

    class Meta:
        db_table = "orders"


class Delivery(models.Model):
    class Type(models.TextChoices):
        PICKUP = "Pickup"
        DELIVERY = "Delivery"

    class Status(models.TextChoices):
        PROCESSING = "Processing"
        HANDOVER = "Handover to delivery"
        IN_TRANSIT = "In transit"
        READY = "Ready for pickup"
        RECEIVED = "Received"

    type = models.CharField(choices=Type)
    status = models.CharField(choices=Status, default=Status.PROCESSING)

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery"
    )

    @override
    def __repr__(self) -> str:
        repr = f"{self.id}, {self.type}, {self.status}, {self.order.customer}"
        return repr

    class Meta:
        db_table = "deliveries"


class Payment(models.Model):
    class Type(models.TextChoices):
        CARD = "Card"
        CASH = "Cash"

    type = models.CharField(choices=Type)
    is_paid = models.BooleanField(default=False)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    @override
    def __repr__(self) -> str:
        repr = f"{self.id}, {self.type}, {self.is_paid}, {self.order.customer}"
        return repr

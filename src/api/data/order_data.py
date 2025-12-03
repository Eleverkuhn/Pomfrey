from datetime import datetime
from typing import override

from django.db import models, transaction

from api.data.base_data import (
    BaseRelationRepository, BaseMainRepository, ModelType
)
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
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)

    @property
    def date_and_time(self) -> datetime:
        return datetime.combine(self.date, self.time)

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


class BaseOrderRelationRepository(BaseRelationRepository[Order]):
    @override
    def __init__(
            self,
            model: type[ModelType],
            model_data: dict,
            related_model: models.Model,
            related_field_name: str = "order"
    ) -> None:
        super().__init__(model, model_data, related_model, related_field_name)


class OrderRepository(BaseMainRepository[Order]):
    @override
    def __init__(self, model_data: dict, model: type[Order] = Order) -> None:
        super().__init__(model, model_data)
        self.related_models = [Delivery, Payment]

    @property
    def delivery_repository(self) -> BaseOrderRelationRepository:
        delivery_repository = self._get_related_repository(
            self.related_models[0], self.model_data["delivery"]
        )
        return delivery_repository

    @property
    def payment_repository(self) -> BaseOrderRelationRepository:
        payment_repository = self._get_related_repository(
            self.related_models[1], self.model_data["payment"]
        )
        return payment_repository

    @override
    @transaction.atomic
    def create(self) -> Order:
        super().create(self.model_data["order"])
        return self.model_instance

    @override
    def _create_relations(self) -> None:
        self.delivery_repository.create()
        self.payment_repository.create()
        self.model_instance.products.set(self.model_data["products"])

    def _get_related_repository(
            self, related_model: type[ModelType], model_data: dict
    ) -> BaseOrderRelationRepository:
        repository = BaseOrderRelationRepository(
            related_model, model_data, self.model_instance
        )
        return repository

from typing import override

from django.db import models

from api.data.base_data import BaseRepository
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


class BaseOrderRelationRepository(BaseRepository):
    @override
    def __init__(
            self, model: type[models.Model], model_data: dict, order: Order
    ) -> None:
        super().__init__(model, model_data)
        self.order = order

    @override
    def create(self) -> models.Model:
        model = self.model(**self.model_data, order=self.order)
        model.save()
        return model


class OrderRepository(BaseRepository[Order]):
    @override
    def __init__(self, model_data: dict, model: type[Order] = Order) -> None:
        super().__init__(model, model_data)
        self.relations_data = self._extract_relations_data()
        self.related_models = [Delivery, Payment]

    @override
    def create(self) -> Order:
        order = super().create()
        self._create_relations(order)
        return order

    def _extract_relations_data(self) -> dict:
        """
        Extracts data for related models 'Product', 'Delivery' and 'Payment'
        into a distinct dictionary and removes it from original 'order_data'
        dict
        """
        relations_data = {
            "products_data": self.model_data.pop("products"),
            "delivery_data": self.model_data.pop("delivery"),
            "payment_data": self.model_data.pop("payment")
        }
        return relations_data

    def _create_relations(self, order: Order) -> None:
        self._create_delivery_instance(order)
        self._create_paymeet_instance(order)
        order.products.set(self.relations_data["products_data"])

    def _create_delivery_instance(self, order: Order) -> None:
        delivery_repository = self._get_delivery_repository(order)
        delivery_repository.create()

    def _get_delivery_repository(
            self, order: Order
    ) -> BaseOrderRelationRepository:
        delivery_repository = BaseOrderRelationRepository(
            self.related_models[0],
            self.relations_data["delivery_data"],
            order
        )
        return delivery_repository

    def _create_paymeet_instance(self, order: Order) -> None:
        payment_repository = self._get_payment_repository(order)
        payment_repository.create()

    def _get_payment_repository(
            self, order: Order
    ) -> BaseOrderRelationRepository:
        payment_repository = BaseOrderRelationRepository(
            self.related_models[1],
            self.relations_data["payment_data"],
            order
        )
        return payment_repository

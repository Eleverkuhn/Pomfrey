from abc import ABC, abstractmethod
from typing import Generic, TypeVar, override

from django.db import models, transaction

from pomfrey_app.models import (
    Customer,
    Order,
    Delivery,
    Payment,
    Pharmacy,
    PharmacyWorkingSchedule
)

ModelType = TypeVar("ModelType", bound=models.Model)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], model_data: dict) -> None:
        self.model: type[ModelType] = model
        self.model_data = model_data

    def create(self, model_data: dict | None = None) -> ModelType:
        model = self._construct_model_instance(model_data)
        model.save()
        return model

    def _construct_model_instance(self, model_data: dict | None) -> ModelType:
        if model_data:
            model = self.model(**model_data)
        else:
            model = self.model(**self.model_data)
        return model


class BaseRelationRepository(BaseRepository, Generic[ModelType]):
    @override
    def __init__(
            self,
            model: type[ModelType],
            model_data: dict,
            related_model: models.Model,
            related_field_name: str
    ) -> None:
        super().__init__(model, model_data)
        self.related_model = related_model
        self.related_field_name = related_field_name

    @property
    def related_field_data(self) -> dict:
        related_field_data = {self.related_field_name: self.related_model}
        return related_field_data

    @override
    def create(self) -> ModelType:
        model = self.model(**self.model_data, **self.related_field_data)
        model.save()
        return model


class BaseMainRepository(ABC, BaseRepository, Generic[ModelType]):
    @override
    @transaction.atomic
    def create(self, model_data: dict | None = None) -> ModelType:
        self.model_instance = super().create(model_data)
        self._create_relations()
        return self.model_instance

    @abstractmethod
    def _create_relations(self) -> None:
        pass


class CustomerRepository(BaseRepository):
    @override
    def __init__(self, model_data: dict, model=Customer) -> None:
        super().__init__(model, model_data)

    @override
    def create(self) -> Customer:
        customer = self.model(email=self.model_data["email"])
        customer.set_password(self.model_data["password"])
        customer.save()
        return customer


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

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, override

from django.db import models, transaction

ModelType = TypeVar("ModelType", bound=models.Model)


class FieldDefault:
    nanoid_size: int = 10
    phone_lenght: int = 10
    title_lenght: int = 30
    decimal_digits: int = 8
    decimal_places: int = 2
    geo_title_length: int = 60
    street_length: int = 30
    apartment_length: int = 15
    postal_code_length: int = 8


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

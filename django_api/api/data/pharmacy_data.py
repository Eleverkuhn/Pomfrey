from typing import override, Generic

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from api.data.base_data import (
    BaseRepository, BaseRelationRepository, ModelType
)
from api.data.geo_data import Address


class Pharmacy(models.Model):
    phone = PhoneNumberField(region="US", null=True)

    address = models.OneToOneField(
        Address, on_delete=models.CASCADE, related_name="address", null=True
    )

    class Meta:
        db_table = "pharmacies"


class PharmacyWorkingSchedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    pharmacies = models.ManyToManyField(Pharmacy, related_name="pharmacies")

    class Meta:
        db_table = "pharmacy_working_schedules"


class PharmacyRepository(BaseRepository):
    @override
    def __init__(
            self, model_data: dict, model: type[Pharmacy] = Pharmacy
    ) -> None:
        super().__init__(model, model_data)

    @property
    def schedule_repository(self) -> "PharmacyWorkingScheduleRepository":
        schedule_repository = PharmacyWorkingScheduleRepository(
            self.model_data["schedule"], self.pharmacy
        )
        return schedule_repository

    @override
    def create(self) -> Pharmacy:
        self.pharmacy = self.model(**self.model_data["pharmacy"])
        self.pharmacy.save()
        self.schedule_repository.create()
        return self.pharmacy


class PharmacyRelationRepository(
        BaseRelationRepository[ModelType], Generic[ModelType]
):
    related_field_name = "pharmacy"

    @override
    def __init__(
            self,
            model: type[ModelType],
            model_data: dict,
            related_model: Pharmacy,
            related_field_name: str = "pharmacy"
    ) -> None:
        super().__init__(model, model_data, related_model, related_field_name)


class PharmacyWorkingScheduleRepository(
        PharmacyRelationRepository[PharmacyWorkingSchedule]
):
    @override
    def __init__(
            self,
            model_data: dict,
            related_model: Pharmacy,
            model: type[PharmacyWorkingSchedule] = PharmacyWorkingSchedule
    ) -> None:
        super().__init__(model, model_data, related_model)

    @override
    def create(self) -> PharmacyWorkingSchedule:
        model = self.model(**self.model_data)
        model.save()
        model.pharmacies.set([self.related_model])
        return model

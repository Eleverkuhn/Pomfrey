from typing import override, Generic

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from api.data.base_data import (
    FieldDefault, BaseRepository, BaseRelationRepository, ModelType
)


class Pharmacy(models.Model):
    phone = PhoneNumberField(region="US", null=True)

    class Meta:
        db_table = "pharmacies"


class PharmacyAddress(models.Model):
    region = models.CharField(max_length=FieldDefault.geo_title_length)
    city = models.CharField(max_length=FieldDefault.geo_title_length)
    street = models.CharField(max_length=FieldDefault.street_length)
    apartment = models.CharField(max_length=FieldDefault.apartment_length)
    postal_code = models.CharField(max_length=FieldDefault.postal_code_length)

    pharmacy = models.OneToOneField(
        Pharmacy,
        on_delete=models.CASCADE,
        related_name="pharmacy",
        null=True
    )

    class Meta:
        db_table = "pharmacy_addresses"

    @override
    def __repr__(self) -> str:
        address_parts = [
            str(self.pharmacy.id),
            self.region,
            self.city,
            self.street,
            self.apartment,
            self.postal_code
        ]
        repr = ", ".join(address_parts)
        return repr


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
    def address_repository(self) -> "PharmacyRelationRepository":
        address_repository = PharmacyRelationRepository(
            PharmacyAddress, self.model_data["address"], self.pharmacy
        )
        return address_repository

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
        self._create_relations()
        return self.pharmacy

    def _create_relations(self) -> None:
        self.address_repository.create()
        self.schedule_repository.create()


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

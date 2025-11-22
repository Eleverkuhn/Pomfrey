from typing import override

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from api.data.base_data import FieldDefault


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
            self.pharmacy.id,
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

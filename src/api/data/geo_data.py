from typing import override

from django.db import models

from api.data.base_data import FieldDefault


class Address(models.Model):
    region = models.CharField(max_length=FieldDefault.geo_title_length)
    city = models.CharField(max_length=FieldDefault.geo_title_length)
    street = models.CharField(max_length=FieldDefault.street_length)
    apartment = models.CharField(max_length=FieldDefault.apartment_length)
    postal_code = models.CharField(max_length=FieldDefault.postal_code_length)

    @property
    def full_address(self) -> str:
        address_parts = [
            self.region,
            self.city,
            self.street,
            self.apartment,
            self.postal_code
        ]
        full_address = ", ".join(address_parts)
        return full_address

    class Meeta:
        db_table = "addresses"

    @override
    def __repr__(self) -> str:
        return self.full_address

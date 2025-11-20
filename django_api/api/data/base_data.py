from django.db import models


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


class ModelAbstract(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        abstract = True

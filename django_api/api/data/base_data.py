from django.db import models


class FieldDefault:
    nanoid_size: int = 10
    phone_lenght: int = 10
    title_lenght: int = 30
    decimal_digits: int = 8
    decimal_places: int = 2


class ModelAbstract(models.Model):
    id = models.IntegerField(primary_key=True)

    class Meta:
        abstract = True

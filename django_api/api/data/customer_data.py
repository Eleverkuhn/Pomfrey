from typing import override

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from nanoid import generate

from api.data.base_data import FieldDefault, BaseRepository


def generate_nanoid(size=FieldDefault.nanoid_size):
    return generate(size=size)


class CustomerManager(BaseUserManager):
    def create_user(
            self, email: str, password=None, **extra_fields
    ) -> "Customer":
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Customer(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(
        primary_key=True,
        default=generate_nanoid,
        max_length=FieldDefault.nanoid_size,
        editable=False
    )
    email = models.EmailField(unique=True)
    objects = CustomerManager()

    USERNAME_FIELD = "email"

    def __str__(self) -> str:
        return f"{self.email}"


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

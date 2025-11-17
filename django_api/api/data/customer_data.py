from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from nanoid import generate

from api.data.base_data import FieldDefault


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

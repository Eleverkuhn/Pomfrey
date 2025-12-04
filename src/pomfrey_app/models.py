from datetime import datetime
from typing import TypeVar, override

from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from nanoid import generate
from phonenumber_field.modelfields import PhoneNumberField

from django.db import models

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


def generate_nanoid(size=FieldDefault.nanoid_size):  # TODO: redundant function, probably need to remove it
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


class ProductAbstract(models.Model):
    title = models.CharField(max_length=FieldDefault.title_lenght)

    class Meta:
        abstract = True


class ProductCategory(ProductAbstract):
    class Meta:
        db_table = "product_categoires"


class ProductType(ProductAbstract):
    categories = models.ManyToManyField(ProductCategory)

    class Meta:
        db_table = "product_types"


class Product(ProductAbstract):
    price = models.DecimalField(
        max_digits=FieldDefault.decimal_digits,
        decimal_places=FieldDefault.decimal_places
    )
    stock = models.IntegerField()

    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    categories = models.ManyToManyField(ProductCategory)

    @override
    def __repr__(self) -> str:
        repr = f"{self.id} {self.title}"
        return repr

    class Meeta:
        db_table = "products"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "Pending"
        RECEIVED = "Received"
        CANCELLED = "Cancelled"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)
    status = models.CharField(choices=Status, default=Status.PENDING)
    date = models.DateField(auto_now=True)
    time = models.TimeField(auto_now=True)

    @property
    def date_and_time(self) -> datetime:
        return datetime.combine(self.date, self.time)

    @override
    def __repr__(self) -> str:
        repr = f"{self.id} {self.customer} ({self.products.all()})"
        return repr

    class Meta:
        db_table = "orders"


class Delivery(models.Model):
    class Type(models.TextChoices):
        PICKUP = "Pickup"
        DELIVERY = "Delivery"

    class Status(models.TextChoices):
        PROCESSING = "Processing"
        HANDOVER = "Handover to delivery"
        IN_TRANSIT = "In transit"
        READY = "Ready for pickup"
        RECEIVED = "Received"

    type = models.CharField(choices=Type)
    status = models.CharField(choices=Status, default=Status.PROCESSING)

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery"
    )

    @override
    def __repr__(self) -> str:
        repr = f"{self.id}, {self.type}, {self.status}, {self.order.customer}"
        return repr

    class Meta:
        db_table = "deliveries"


class Payment(models.Model):
    class Type(models.TextChoices):
        CARD = "Card"
        CASH = "Cash"

    type = models.CharField(choices=Type)
    is_paid = models.BooleanField(default=False)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)

    @override
    def __repr__(self) -> str:
        repr = f"{self.id}, {self.type}, {self.is_paid}, {self.order.customer}"
        return repr

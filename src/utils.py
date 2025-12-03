"""
This module provides various utilities for the project purposes
"""

import json
import random
from datetime import time
from decimal import Decimal
from typing import override

from faker import Faker
from psycopg import Cursor
from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from knox.models import AuthToken

from logger.setup import LoggingConfig
from api.service.customer_services import RegistryService
from api.data.base_data import BaseRepository
from api.data.customer_data import Customer, CustomerRepository
from api.data.pharmacy_data import (
    Pharmacy,
    PharmacyRepository,
)
from api.data.product_data import ProductCategory, ProductType, Product
from api.data.order_data import Delivery, Payment
from api.data.geo_data import Address


class BaseDatabaseTest:
    def execute_test_query(self, cursor: Cursor) -> None:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)


class UtilsTest:
    """
    A set of helping functions for setting up test data
    """
    def _create_auth_header(self) -> str:
        auth_token = AuthToken.objects.create(user=self.customer)[1]
        auth_header = f"Token {auth_token}"
        return auth_header


class BaseTestWithCustomer:
    @staticmethod
    def generate_login_data() -> dict:
        login_data = CustomerTestData().generate_login_data()
        return login_data

    @staticmethod
    def create_customer(model_data: dict | None = None) -> Customer:
        customer = CustomerTestData(model_data).create_customer()
        return customer


class BaseAuthTest(TestCase, BaseTestWithCustomer):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        cls.customer_data = cls.generate_login_data()


class BaseTestWithCreatedCustomer(BaseAuthTest, UtilsTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.customer = cls.create_customer(cls.customer_data)


class BaseTestWithAuthenticationHeader(BaseTestWithCreatedCustomer):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.auth_header = self._create_auth_header()


class BaseRegistryTest(BaseAuthTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls._add_confirm_password_field()
        cls.service = RegistryService(cls.customer_data)

    @classmethod
    def _add_confirm_password_field(cls) -> None:
        update_data = {"confirm_password": cls.customer_data["password"]}
        cls.customer_data.update(update_data)


class BaseLogoutTest(UtilsTest):
    def _check_auth_token_is_valid(self, url: str, auth_header: str) -> None:
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _check_token_is_removed(self, url: str, auth_header: str) -> None:
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BaseViewTest:
    def _convert_response_to_json(self, response: Response) -> dict:
        decoded_response = response.content.decode("utf-8")
        content = json.loads(decoded_response)
        return content


class BaseOrderTest(BaseTestWithCreatedCustomer):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.pharmacy = PharmacyTestData().create_pharmacy()
        cls.product_ids = ProductTestData().product_ids
        cls.order_data = cls.generate_model_data()

    @classmethod
    def generate_model_data(cls) -> dict:
        model_data = {
            "order": cls._generate_order_data(),
            "products": cls.product_ids,
            "delivery": cls._generate_delivery_data(),
            "payment": cls._generate_payment_data()
        }
        return model_data

    @classmethod
    def _generate_order_data(cls) -> dict:
        order = {
            "customer": cls.customer.id,
            "pharmacy": cls.pharmacy.id
        }
        return order

    @staticmethod
    def _generate_delivery_data() -> dict:
        delivery_data = {"type": Delivery.Type.DELIVERY}
        return delivery_data

    @staticmethod
    def _generate_payment_data() -> dict:
        payment_data = {"type": Payment.Type.CARD, "is_paid": True}
        return payment_data


class CustomerTestData:
    def __init__(self, model_data: dict | None = None) -> None:
        self.model_data = model_data
        self.faker = Faker()

    def create_customer(self) -> Customer:
        self._generate_and_set_model_data_if_not_provided()
        customer = CustomerRepository(self.model_data).create()
        return customer

    def _generate_and_set_model_data_if_not_provided(self) -> None:
        if not self.model_data:
            self.model_data = self.generate_login_data()

    def generate_login_data(self) -> dict[str, str]:
        login_data = {
            "email": self.faker.email(),
            "password": self.faker.password(
                length=10,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
            )
        }
        return login_data

    def _create_customer_in_db(self, login_data: dict[str, str]) -> Customer:
        customer = Customer(email=login_data.get("email"))
        customer.set_password(login_data.get("password"))
        customer.save()
        return customer


class LocaleTestData:
    """
    Test data for a specific location
    """
    def __init__(self, locale: str = "en_US", **kwargs) -> None:
        super().__init__(**kwargs)
        self.faker = Faker(locale)


class AddressTestData(LocaleTestData):
    model = Address

    @property
    def address_repository(self) -> BaseRepository:
        address_repository = BaseRepository(
            self.model, self.generate_model_data()
        )
        return address_repository

    def create_address(self) -> Address:
        address = self.address_repository.create()
        return address

    def generate_model_data(self) -> dict[str, str]:
        pharmacy_address_data = self._generate_raw_pharmacy_address_data()
        pharmacy_address_data = self._truncate_field_data(pharmacy_address_data)
        return pharmacy_address_data

    def _generate_raw_pharmacy_address_data(self) -> dict[str, str]:
        pharmacy_address_data = {
            "region": self.faker.state(),
            "city": self.faker.city(),
            "street": self.faker.street_address(),
            "apartment": self.faker.secondary_address(),
            "postal_code": self.faker.postcode()
        }
        return pharmacy_address_data

    def _truncate_field_data(
            self, pharmacy_address_data: dict[str, str]
    ) -> dict[str, str]:
        truncated_pharmacy_address_data = {
            key: value[:self._get_field_max_length(key)]
            for key, value
            in pharmacy_address_data.items()
        }
        return truncated_pharmacy_address_data

    def _get_field_max_length(self, field_name: str) -> int:
        field_max_length = self.model._meta.get_field(field_name).max_length
        return field_max_length


class PharmacyTestData(LocaleTestData):
    @override
    def __init__(self) -> None:
        super().__init__()
        self.address = AddressTestData().create_address()
        self.schedule_test_data = PharmacyWorkingScheduleTestData()

    @property
    def pharmacy_repository(self) -> PharmacyRepository:
        pharmacy_repository = PharmacyRepository(self.generate_model_data())
        return pharmacy_repository

    def create_pharmacy(self) -> Pharmacy:
        pharmacy = self.pharmacy_repository.create()
        return pharmacy

    def generate_model_data(self) -> dict:
        model_data = {
            "pharmacy": {
                "phone": self.faker.phone_number(),
                "address": self.address
            },
            "schedule": self.schedule_test_data.generate_model_data()
        }
        return model_data


class PharmacyWorkingScheduleTestData:
    START_HOUR = 8
    END_HOUR = 20

    def generate_model_data(self) -> dict:
        test_data = {
            "start_time": time(hour=self.START_HOUR),
            "end_time": time(hour=self.END_HOUR)
        }
        return test_data


class ProductTestData:
    MIN_STOCK = 1
    MAX_STOCK = 2
    MIN_PRICE = 100
    MAX_PRICE = 1000000

    def __init__(self) -> None:
        self.category_test_data = ProductCategoryTestData()
        self.type_test_data = ProductTypeTestData()
        self.faker = Faker()

    @property
    def categories_to_types(self) -> dict[str, list[str]]:
        c = self.category_test_data.categories
        t = self.type_test_data.types
        cateogries_to_types = {
            c[0]: [t[2], t[13], t[6]],
            c[1]: [t[16], t[25], t[3], t[14]],
            c[2]: [t[22], t[11], t[21], t[2]],
            c[3]: [t[17], t[10], t[2]],
            c[4]: [t[20], t[25]],
            c[5]: [t[6], t[20]],
            c[6]: [t[1], t[0], t[8]],
            c[7]: [t[2], t[2]],
            c[8]: [t[2], t[2]],
            c[9]: [t[24], t[12], t[4]],
            c[10]: [t[2], t[2], t[7], t[3], t[15]],
            c[11]: [t[18], t[19], t[5]],
            c[12]: [t[3], t[14], t[7]],
            c[13]: [t[2], t[9], t[2], t[16]],
            c[14]: [t[2], t[2], t[3]],
        }
        return cateogries_to_types

    @property
    def random_title(self) -> str:
        title = self.faker.word().capitalize()
        return title

    @property
    def random_category(self) -> str:
        category = random.choice(list(self.categories_to_types.keys()))
        return category

    @property
    def random_stock(self) -> int:
        stock = random.randint(self.MIN_STOCK, self.MAX_STOCK)
        return stock

    @property
    def random_price(self) -> Decimal:
        price = Decimal(random.randint(self.MIN_PRICE, self.MAX_PRICE))
        return price

    @property
    def price_divider(self) -> Decimal:
        divider = Decimal(100)
        return divider

    @property
    def product_ids(self) -> list[int]:
        ids = [product.id for product in self.create_multiple_products()]
        return ids

    def create_multiple_products(self, amount: int = 3) -> list[Product]:
        products = [self.create_product() for _ in range(amount)]
        return products

    def create_product(self) -> Product:
        category, product_type = self._create_category_and_product_type()
        product = Product(
            title=self._generate_title(product_type.title),
            type=product_type,
            stock=self.random_stock,
            price=self._generate_price()
        )
        product.save()
        product.categories.set([category])
        return product

    def _create_category_and_product_type(self) -> tuple[
            ProductCategory, ProductType
    ]:
        category = ProductCategoryTestData().create_category(
            self.random_category
        )
        product_type = ProductTypeTestData().create_type(
            random.choice(self.categories_to_types[category.title]),
            category
        )
        return (category, product_type)

    def _generate_title(self, product_type: str) -> str:
        title = f"{self.random_title} {product_type}"
        return title

    def _generate_price(self) -> Decimal:
        price = self.random_price / self.price_divider
        return price


class ProductCategoryTestData:
    categories = [
        "Allergy",
        "Baby Care",
        "Cold & Flu",
        "Digestive Health",
        "Diabetes Care",
        "Eye Care",
        "First Aid",
        "Heart Health",
        "Men’s Health",
        "Oral Care",
        "Pain Relief",
        "Personal Care",
        "Skin Care",
        "Vitamins & Supplements",
        "Women’s Health"
    ]

    def create_category(self, title: str) -> ProductCategory:
        category = ProductCategory.objects.create(title=title)
        return category

    def create_categories(self) -> None:  # NOTE: not used, but can be used later
        for category in self.categories:
            ProductCategory.objects.create(title=category)


class ProductTypeTestData:
    types = [
        "Antiseptic",
        "Bandages",
        "Capsules",
        "Cream",
        "Dental Floss",
        "Deodorant",
        "Eye Drops",
        "Gel",
        "Gauze",
        "Gummies",
        "Liquid",
        "Lozenges",
        "Mouthwash",
        "Nasal Spray",
        "Ointment",
        "Patch",
        "Powder",
        "Probiotics",
        "Shampoo",
        "Soap",
        "Solution",
        "Spray",
        "Syrup",
        "Tablets",
        "Toothpaste",
        "Wipes",
    ]

    def create_type(
            self, product_type: str, category: ProductCategory
    ) -> ProductType:
        product_type = ProductType(title=product_type)
        product_type.save()
        product_type.categories.set([category])
        return product_type

    def create_types(self) -> None:  # NOTE: not used, but can be used later
        for product_type in self.types:
            ProductType.objects.create(title=product_type)

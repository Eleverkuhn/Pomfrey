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
from api.service.base_services import BaseService
from api.data.customer_data import Customer
from api.data.pharmacy_data import (
    PharmacyAddress, PharmacyWorkingSchedule, Pharmacy
)
from api.data.product_data import ProductCategory, ProductType, Product


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


class BaseAuthTest(TestCase):
    def setUp(self) -> None:
        self.customer_test_data = CustomerTestData()
        self.data = self.customer_test_data.generate_login_data()


class BaseTestWithCreatedCustomer(BaseAuthTest, UtilsTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.customer = self.customer_test_data.create_customer(self.data)


class BaseTestWithAuthenticationHeader(BaseTestWithCreatedCustomer):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.auth_header = self._create_auth_header()


class BaseTestService(UtilsTest):
    service_class: type[BaseService]

    def setUp(self) -> None:
        super().setUp()
        self.service = self.service_class(self.data)


class BaseRegistryTest(BaseAuthTest):
    def setUp(self) -> None:
        super().setUp()
        self.data.update({"confirm_password": self.data.get("password")})


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
    def setUp(self) -> None:
        super().setUp()
        self.pharmacy = PharmacyTestData().create_pharmacy()
        self.order_data = {
            "customer": self.customer.id,
            "pharmacy": self.pharmacy.id,
            "products": ProductTestData().product_ids
        }


class CustomerTestData:
    def __init__(self) -> None:
        self.faker = Faker()

    def create_customer(
            self, login_data: dict[str, str] | None = None
    ) -> Customer:
        login_data = self._generate_login_data_if_not_provided(login_data)
        customer = self._create_customer_in_db(login_data)
        return customer

    def _generate_login_data_if_not_provided(
            self, login_data: dict[str, str] | None
    ) -> dict[str, str]:
        if not login_data:
            login_data = self.generate_login_data()
        return login_data

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


class PharmacyTestData:
    def __init__(self) -> None:
        self.address_test_data = PharmacyAddressTestData()
        self.working_schedule_test_data = PharmacyWorkingScheduleTestData()

    def create_pharmacy(self) -> Pharmacy:
        address, working_schedule = self.create_related_table_entries()
        pharmacy = Pharmacy.objects.create(
            address=address, working_schedule=working_schedule
        )
        return pharmacy

    def create_related_table_entries(
            self
    ) -> tuple[PharmacyAddress, PharmacyWorkingSchedule]:
        address = self.address_test_data.create_pharamacy_address()
        schedule = self.working_schedule_test_data.create_pharmacy_working_schedule()
        return (address, schedule)


class PharmacyAddressTestData:
    def __init__(self, locale_code: str = "en_US") -> None:
        self.faker = Faker(locale_code)
        self.model = PharmacyAddress

    def create_pharamacy_address(self) -> PharmacyAddress:
        pharmacy_address_data = self.generate_pharmacy_address_data()
        pharmacy_address = self.model.objects.create(**pharmacy_address_data)
        return pharmacy_address

    def generate_pharmacy_address_data(self) -> dict[str, str]:
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


class PharmacyWorkingScheduleTestData:
    def __init__(self, start_hour: int = 8, end_hour: int = 20) -> None:
        self.start_hour = start_hour
        self.end_hour = end_hour

    def create_pharmacy_working_schedule(self) -> PharmacyWorkingSchedule:
        pharmacy_working_schedule = PharmacyWorkingSchedule.objects.create(
            start_time=time(hour=self.start_hour),
            end_time=time(hour=self.end_hour)
        )
        return pharmacy_working_schedule


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

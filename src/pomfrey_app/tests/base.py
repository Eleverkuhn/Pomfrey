"""
This module contains base test cases for tests
"""

from typing import override

from django.test import Client
from psycopg import Cursor

from utils import UtilsTest
from pomfrey_app.services import RegistryService
from pomfrey_app.models import (
    Customer,
    Pharmacy,
    Product,
    Delivery,
    Payment
)


class FixtureCustomer:
    fixtures = ["customers"]


class FixtureProduct:
    fixtures = [
        "customers",
        "addresses",
        "pharmacies",
        "product_categories",
        "product_types",
        "products"
    ]


class TestWithClient:
    """Need to make a request on a class level"""
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.client = Client()


class TestWithLoginData(UtilsTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        cls.customer_data = cls.generate_login_data()


class TestWithCreatedCustomers(UtilsTest):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.customer = Customer.objects.get(id="N5QDXIQ8R_")


class BaseDatabaseTest:
    def execute_test_query(self, cursor: Cursor) -> None:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)


class BaseRegistryTest(TestWithLoginData):
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


class BaseLoginTest(TestWithClient, TestWithLoginData):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.customer = cls.create_customer(cls.customer_data)


class BaseProtectedViewTest(FixtureCustomer, TestWithCreatedCustomers):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.auth_header = cls.create_auth_header()


class BaseOrderTest(FixtureProduct, TestWithClient, TestWithCreatedCustomers):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.pharmacy = Pharmacy.objects.get(id=1)
        cls.order_data = cls.generate_model_data()

    @classmethod
    def generate_model_data(cls) -> dict:
        model_data = {
            "order": cls._generate_order_data(),
            "products": cls._get_products(),
            "delivery": cls._generate_delivery_data(),
            "payment": cls._generate_payment_data()
        }
        return model_data

    @classmethod
    def _generate_order_data(cls) -> dict:
        return {"customer": cls.customer.id, "pharmacy": cls.pharmacy.id}

    @classmethod
    def _get_products(cls) -> list[int]:
        return [Product.objects.get(id=1).id, Product.objects.get(id=2).id]

    @staticmethod
    def _generate_delivery_data() -> dict:
        return {"type": Delivery.Type.DELIVERY}

    @staticmethod
    def _generate_payment_data() -> dict:
        return {"type": Payment.Type.CARD, "is_paid": True}

"""
This module provides various utilities for the project purposes
"""

from django.test import TestCase
from psycopg import Cursor

from api.service.base_services import BaseService
from api.data.customer_data import Customer


class BaseDatabaseTest:
    def execute_test_query(self, cursor: Cursor) -> None:
        cursor.execute("SELECT 1;")
        row = cursor.fetchone()
        self.assertEqual(row[0], 1)


class UtilsTest:
    """
    A set of helping functions for setting up test data
    """
    def _create_customer(self) -> Customer:
        customer = Customer(email=self.data.get("email"))
        customer.set_password(self.data.get("password"))
        customer.save()
        return customer


class BaseTestService(UtilsTest):
    service_class: type[BaseService]

    def setUp(self) -> None:
        super().setUp()
        self.service = self.service_class(self.data)


class BaseLoginTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "email": f"test_{self._testMethodName}@example.com",
            "password": "ComplicatedP@sSw0rd",
        }


class BaseRegistryTest(BaseLoginTest):
    def setUp(self) -> None:
        super().setUp()
        self.data.update({"confirm_password": self.data.get("password")})

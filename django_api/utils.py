"""
This module provides various utilities for the project purposes
"""

from typing import override

from django.test import TestCase
from rest_framework import status
from psycopg import Cursor
from knox.models import AuthToken

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

    def _create_auth_header(self) -> str:
        auth_token = AuthToken.objects.create(self.customer)[1]
        auth_header = f"Token {auth_token}"
        return auth_header


class BaseAuthTest(TestCase):
    def setUp(self) -> None:
        self.data = {
            "email": f"test_{self._testMethodName}@example.com",
            "password": "ComplicatedP@sSw0rd",
        }


class BaseTestWithCreatedCustomer(BaseAuthTest, UtilsTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.customer = self._create_customer()


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

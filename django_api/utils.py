"""
This module provides various utilities for the project purposes
"""

import json
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
        self.customer_generator = TestCustomerGenerator()
        self.data = self.customer_generator.generate_login_data()


class BaseTestWithCreatedCustomer(BaseAuthTest, UtilsTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.customer = self.customer_generator.generate_customer()


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


class TestCustomerGenerator:
    def __init__(self) -> None:
        self.faker = Faker()

    def generate_customer(self) -> Customer:
        customer = self._create_customer()
        return customer

    def generate_login_data(self) -> dict[str, str]:
        self.login_data = {
            "email": self.faker.email(),
            "password": self.faker.password(
                length=10,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
            )
        }
        return self.login_data

    def _create_customer(self) -> Customer:
        customer = Customer(email=self.login_data.get("email"))
        customer.set_password(self.login_data.get("password"))
        customer.save()
        return customer


class BaseOrderTest(BaseTestWithCreatedCustomer):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.order_data = {
            "customer": 1,
            "pharmacy": 1,
            "products": [1, 2, 3]
        }
        self.fake = Faker("en_US")
        self.pharmacy = self._create_pharmacy()

    def _create_order(self) -> None:
        pass

    def _create_pharmacy(self) -> None:
        pharmacy_address = PharmacyAddress.objects.create(
            region=self.fake.state()[:PharmacyAddress._meta.get_field("region").max_length],
            city=self.fake.city()[:PharmacyAddress._meta.get_field("city").max_length],
            street=self.fake.street_address()[:PharmacyAddress._meta.get_field("street").max_length],
            apartment=self.fake.secondary_address()[:PharmacyAddress._meta.get_field("apartment").max_length],
            postal_code=self.fake.postcode()[:PharmacyAddress._meta.get_field("postal_code").max_length]
        )
        LoggingConfig().logger.debug("%r", pharmacy_address)
        return pharmacy_address

    def _cretat_products(self) -> None:
        pass

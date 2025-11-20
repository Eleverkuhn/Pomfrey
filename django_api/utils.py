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
        self.order_data = {
            "customer": 1,
            "pharmacy": 1,
            "products": [1, 2, 3]
        }
        self.pharmacy_address = PharmacyAddressTestData().create_pharamacy_address()
        LoggingConfig().logger.debug("%r", self.pharmacy_address)

    def _create_order(self) -> None:
        pass

    def _cretat_products(self) -> None:
        pass


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
    pass


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

"""
This module provides various utilities for the project purposes
"""

import json

from faker import Faker
from django.test import TestCase
from rest_framework.response import Response
from knox.models import AuthToken

from pomfrey_app.models import Customer
from pomfrey_app.model_repositories import CustomerRepository


class UtilsTest(TestCase):
    """
    A set of helping functions for setting up test data
    """
    @staticmethod
    def generate_login_data() -> dict:
        login_data = CustomerTestData().generate_login_data()
        return login_data

    @staticmethod
    def create_customer(model_data: dict | None = None) -> Customer:
        customer = CustomerTestData(model_data).create_customer()
        return customer

    @staticmethod
    def convert_response_to_json(response: Response) -> dict:
        decoded_response = response.content.decode("utf-8")
        content = json.loads(decoded_response)
        return content

    @classmethod
    def create_auth_header(cls) -> str:
        auth_token = AuthToken.objects.create(user=cls.customer)[1]
        auth_header = f"Token {auth_token}"
        return auth_header


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

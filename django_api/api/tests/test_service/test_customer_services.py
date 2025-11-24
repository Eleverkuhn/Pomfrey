from typing import override

from rest_framework.validators import ValidationError

from utils import (
    BaseTestWithCreatedCustomer,
    BaseAuthTest,
    BaseRegistryTest
)
from logger.setup import LoggingConfig
from api.service.customer_services import LoginService, RegistryService
from api.data.customer_data import Customer


class TestRegistryService(BaseRegistryTest):
    # @override
    # @classmethod
    # def setUpTestData(cls) -> None:
    #     super().setUpTestData()
    #     cls._add_confirm_password_field()
    #     cls.service = RegistryService(cls.customer_data)

    # @classmethod
    # def _add_confirm_password_field(cls) -> None:
    #     update_data = {"confirm_password": cls.customer_data["password"]}
    #     cls.customer_data.update(update_data)

    def test_exec_creates_new_customer(self) -> None:
        email = self.customer_data["email"]

        self.service.exec()
        customer_db = Customer.objects.get(email=email)

        self.assertEqual(customer_db.email, email)
        customer_db.delete()

    def test_validate_succeed(self) -> None:
        validated_data = self.service.validate()
        self.assertEqual(validated_data, self.customer_data)
        LoggingConfig().get_logger().debug(validated_data)

    def test_validation_fails_for_non_unique_email(self) -> None:
        self.create_customer(self.customer_data)
        with self.assertRaises(ValidationError) as cm:
            self.service.validate()
        self.assertTrue(cm.exception.get_full_details().get("email"))


class TestLoginService(BaseTestWithCreatedCustomer):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.service = LoginService(cls.customer_data)

    def test_exec_returns_email_with_auth_token(self) -> None:
        response_data = self.service.exec()
        self.assertEqual(response_data["email"], self.customer_data["email"])
        self.assertTrue(response_data["token"])

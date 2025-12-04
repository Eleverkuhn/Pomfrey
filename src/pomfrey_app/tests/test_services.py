from rest_framework.validators import ValidationError

from logger.setup import LoggingConfig
from pomfrey_app.services import LoginService
from pomfrey_app.models import Customer
from pomfrey_app.tests.base import BaseLoginTest, BaseRegistryTest


class TestRegistryService(BaseRegistryTest):
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


class TestLoginService(BaseLoginTest):
    def test_exec_returns_email_with_auth_token(self) -> None:
        response_data = LoginService(self.customer_data).exec()
        self.assertEqual(response_data["email"], self.customer_data["email"])
        self.assertTrue(response_data["token"])

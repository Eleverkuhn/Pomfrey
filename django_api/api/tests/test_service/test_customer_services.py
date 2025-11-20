from rest_framework.validators import ValidationError

from utils import (
    BaseTestWithCreatedCustomer,
    BaseRegistryTest,
    BaseTestService
)
from logger.setup import LoggingConfig
from api.service.customer_services import RegistryService, LoginService
from api.data.customer_data import Customer


class TestRegistryService(BaseTestService, BaseRegistryTest):
    service_class = RegistryService

    def test_exec_creates_new_customer(self) -> None:
        email = self.data.get("email")

        self.service.exec()
        customer_db = Customer.objects.get(email=email)

        self.assertEqual(customer_db.email, email)
        customer_db.delete()

    def test_validate_succeed(self) -> None:
        validated_data = self.service.validate()
        self.assertEqual(validated_data, self.data)
        LoggingConfig().get_logger().debug(validated_data)

    def test_validation_fails_for_non_unique_email(self) -> None:
        self.customer_generator.generate_customer()
        with self.assertRaises(ValidationError) as cm:
            self.service.validate()
        self.assertTrue(cm.exception.get_full_details().get("email"))


class TestLoginService(BaseTestService, BaseTestWithCreatedCustomer):
    service_class = LoginService

    def test_exec_returns_email_with_auth_token(self) -> None:
        response_data = self.service.exec()
        self.assertEqual(response_data.get("email"), self.data.get("email"))
        self.assertTrue(response_data.get("token"))

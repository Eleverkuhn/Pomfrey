from rest_framework.validators import ValidationError

from utils import BaseRegistryTest
from logger.setup import LoggingConfig
from api.service.customer_services import RegistryService
from api.data.customer_data import Customer


class TestRegistryService(BaseRegistryTest):
    def setUp(self) -> None:
        super().setUp()
        self.service = RegistryService(self.data)

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
        Customer.objects.create(
            email=self.data.get("email"),
            password=self.data.get("password")
        )
        with self.assertRaises(ValidationError) as cm:
            self.service.validate()
        self.assertTrue(cm.exception.get_full_details().get("email"))

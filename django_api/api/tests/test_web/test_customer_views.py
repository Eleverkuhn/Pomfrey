import json

from django.urls import reverse
from django.contrib.auth.password_validation import (
    MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator
)
from rest_framework.response import Response

from utils import BaseLoginTest, BaseRegistryTest, UtilsTest
from logger.setup import LoggingConfig
from api.data.customer_data import Customer
from api.web.serializers.customer_serializers import PasswordMatchesValidator


class BaseRegistryViewTest(BaseRegistryTest):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("registry")


class TestRegistry(BaseRegistryViewTest):
    def test_returns_201_created_on_success(self) -> None:
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)

    def test_creates_customer(self) -> None:
        self.client.post(self.url, data=self.data)
        customer_db = Customer.objects.get(email=self.data.get("email"))
        self.assertTrue(customer_db)


class TestValidationErrorRender(BaseRegistryViewTest):
    def setUp(self) -> None:
        super().setUp()

    def test_returns_validation_err_msg_for_short_password(self) -> None:
        self._validation_err_msg_in_response_content(
            "1", MinimumLengthValidator()
        )

    def test_returns_validation_err_msg_for_common_password(self) -> None:
        self._validation_err_msg_in_response_content(
            "password123", CommonPasswordValidator()
        )

    def test_returns_validation_err_msg_for_numeric_password(self) -> None:
        self._validation_err_msg_in_response_content(
            "012345678", NumericPasswordValidator()
        )

    def test_returns_validation_err_msg_if_passwords_do_not_match(self) -> None:
        self._validation_err_msg_in_response_content(
            self.data.get("password"),
            PasswordMatchesValidator("password"),
            "unmatched_password"
        )

    def _validation_err_msg_in_response_content(
            self,
            password: str,
            validator,
            wrong_confirm_password: str | None = None
    ) -> None:
        self._check_wrong_confirm_password(password, wrong_confirm_password)
        response_content = self._get_response_content()
        err_msg = validator.get_error_message()

        self.assertIn(err_msg, response_content)

    def _check_wrong_confirm_password(
            self, password: str, wrong_confirm_password : str | None = None
    ) -> None:
        if wrong_confirm_password:
            self._update_password(password, wrong_confirm_password)
        else:
            self._update_password(password, password)

    def _update_password(self, password: str, confirm_password: str) -> None:
        self.data.update({
            "password": password, "confirm_password": confirm_password
        })

    def _get_response_content(self) -> str:
        response = self.client.post(self.url, self.data)
        response_content = response.content.decode("utf-8")
        return response_content


class TestLogin(BaseLoginTest, UtilsTest):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("login")
        self.customer = self._create_customer()

    def test_returns_200_on_succeed(self) -> None:
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, 200)

    def test_returns_user_with_token(self) -> None:
        response = self.client.post(self.url, self.data)
        response_content = self._get_response_content(response)
        self.assertEqual(response_content.get("email"), self.data.get("email"))
        self.assertTrue(response_content.get("token"))

    def _get_response_content(self, response: Response) -> dict:
        decoded_response = response.content.decode("utf-8")
        content = json.loads(decoded_response)
        return content

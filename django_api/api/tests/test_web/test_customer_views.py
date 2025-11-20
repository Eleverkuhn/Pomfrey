from typing import override

from django.urls import reverse
from django.contrib.auth.password_validation import (
    MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator
)
from rest_framework import status

from utils import (
    BaseTestWithCreatedCustomer,
    BaseTestWithAuthenticationHeader,
    BaseRegistryTest,
    BaseLogoutTest,
    BaseViewTest
)
from api.data.customer_data import Customer
from api.web.serializers.customer_serializers import PasswordMatchesValidator


class BaseRegistryViewTest(BaseRegistryTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("registry")


class TestRegistry(BaseRegistryViewTest):
    def test_returns_201_created_on_success(self) -> None:
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_creates_customer(self) -> None:
        self.client.post(self.url, data=self.data)
        customer_db = Customer.objects.get(email=self.data.get("email"))
        self.assertTrue(customer_db)


class TestValidationErrorRender(BaseRegistryViewTest):
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


class TestLogin(BaseTestWithCreatedCustomer, BaseViewTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("login")

    def test_returns_200_on_succeed(self) -> None:
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_user_with_token(self) -> None:
        response = self.client.post(self.url, self.data)
        response_content = self._convert_response_to_json(response)
        self.assertEqual(response_content.get("email"), self.data.get("email"))
        self.assertTrue(response_content.get("token"))


class TestCustomerPage(BaseTestWithAuthenticationHeader):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("my")

    def test_returns_401_unauthorized_for_unlogged_in_customer(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_200_OK_for_logged_in_customer(self) -> None:
        response = self.client.get(
            self.url, HTTP_AUTHORIZATION=self.auth_header
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestLogout(BaseTestWithAuthenticationHeader, BaseLogoutTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("logout")

    def test_logout_works_as_expected(self) -> None:
        my_url = reverse("my")
        self._check_auth_token_is_valid(my_url, self.auth_header)
        self.client.post(self.url, HTTP_AUTHORIZATION=self.auth_header)
        self._check_token_is_removed(my_url, self.auth_header)


class TestLogoutAll(BaseTestWithCreatedCustomer, BaseLogoutTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("logout_all")

    def test_logout_all_works_as_expected(self) -> None:
        auth_tokens = self._create_multiple_auth_tokens()
        self._check_all_auth_tokens_are_valid(auth_tokens)

        self.client.post(self.url, HTTP_AUTHORIZATION=auth_tokens[0])

        self._check_all_auth_tokens_are_removed(auth_tokens)

    def _create_multiple_auth_tokens(self) -> list[str]:
        auth_tokens = [self._create_auth_header() for _ in range(5)]
        return auth_tokens

    def _check_all_auth_tokens_are_valid(
            self, auth_tokens: list[str]
    ) -> None:
        for token in auth_tokens:
            self._check_auth_token_is_valid(reverse("my"), token)

    def _check_all_auth_tokens_are_removed(
            self, auth_tokens: list[str]
    ) -> None:
        for token in auth_tokens:
            self._check_token_is_removed(reverse("my"), token)

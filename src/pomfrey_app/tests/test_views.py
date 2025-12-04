import json
from typing import override

from django.urls import reverse
from django.contrib.auth.password_validation import (
    MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator
)
from rest_framework import status

from pomfrey_app.tests.base import (
    BaseRegistryTest,
    BaseLoginTest,
    BaseProtectedViewTest,
    BaseOrderTest,
)
from pomfrey_app.models import Customer, Order, Delivery
from pomfrey_app.serializers import PasswordMatchesValidator


class BaseRegistryViewTest(BaseRegistryTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("registry")


class BaseLogoutTest(BaseProtectedViewTest):
    def setUp(self) -> None:
        self.my_url = reverse("my")

    def _check_auth_token_is_valid(self, url: str, auth_header: str) -> None:
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _check_token_is_removed(self, url: str, auth_header: str) -> None:
        response = self.client.get(url, HTTP_AUTHORIZATION=auth_header)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestRegistryView(BaseRegistryViewTest):
    def test_returns_201_created_on_success(self) -> None:
        response = self.client.post(self.url, data=self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_creates_customer(self) -> None:
        self.client.post(self.url, data=self.customer_data)
        customer_db = Customer.objects.get(email=self.customer_data["email"])
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
            self.customer_data["password"],
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
            self, password: str, wrong_confirm_password: str | None = None
    ) -> None:
        if wrong_confirm_password:
            self._update_password(password, wrong_confirm_password)
        else:
            self._update_password(password, password)

    def _update_password(self, password: str, confirm_password: str) -> None:
        update_data = {
            "password": password, "confirm_password": confirm_password
        }
        self.customer_data.update(update_data)

    def _get_response_content(self) -> str:
        response = self.client.post(self.url, self.customer_data)
        response_content = response.content.decode("utf-8")
        return response_content


class TestLoginView(BaseLoginTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        url = reverse("login")
        # client = Client()
        cls.response = cls.client.post(url, cls.customer_data)

    def test_returns_200_on_succeed(self) -> None:
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)

    def test_returns_user_with_token(self) -> None:
        response_content = self.convert_response_to_json(self.response)
        self.assertEqual(response_content["email"], self.customer_data["email"])
        self.assertTrue(response_content["token"])


class TestCustomerPage(BaseProtectedViewTest):
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


class TestLogoutView(BaseLogoutTest):
    def test_logout_works_as_expected(self) -> None:
        self._check_auth_token_is_valid(self.my_url, self.auth_header)
        self.client.post(reverse("logout"), HTTP_AUTHORIZATION=self.auth_header)
        self._check_token_is_removed(self.my_url, self.auth_header)


class TestLogoutAll(BaseLogoutTest):
    def test_logout_all_works_as_expected(self) -> None:
        auth_tokens = self._create_multiple_auth_tokens()
        self._check_all_auth_tokens_are_valid(auth_tokens)

        self.client.post(
            reverse("logout_all"), HTTP_AUTHORIZATION=auth_tokens[0]
        )

        self._check_all_auth_tokens_are_removed(auth_tokens)

    def _create_multiple_auth_tokens(self) -> list[str]:
        auth_tokens = [self.create_auth_header() for _ in range(5)]
        return auth_tokens

    def _check_all_auth_tokens_are_valid(
            self, auth_tokens: list[str]
    ) -> None:
        for token in auth_tokens:
            self._check_auth_token_is_valid(self.my_url, token)

    def _check_all_auth_tokens_are_removed(
            self, auth_tokens: list[str]
    ) -> None:
        for token in auth_tokens:
            self._check_token_is_removed(self.my_url, token)


class TestOrderView(BaseOrderTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        request_data = json.dumps(cls.order_data)
        cls.response = cls.client.post(
            reverse("order"),
            data=request_data,
            content_type="application/json"
        )
        cls.response_content = cls.convert_response_to_json(cls.response)

    def test_returns_201_CREATED_on_success(self) -> None:
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_order_id_in_response(self) -> None:
        self.assertTrue(self.response_content.get("id"))

    def test_customer_in_response(self) -> None:
        customer = self.response_content["customer"]
        self.assertEqual(customer["id"], self.order_data["order"]["customer"])
        self.assertEqual(customer["email"], self.customer.email)

    def test_status_in_response(self) -> None:
        self.assertEqual(self.response_content["status"], Order.Status.PENDING)

    def test_pharmacy_in_response(self) -> None:
        pharmacy = self.response_content["pharmacy"]
        address = ", ".join(pharmacy["address"].values())
        self.assertEqual(pharmacy["phone"], self.pharmacy.phone)
        self.assertEqual(address, self.pharmacy.address.full_address)

    def test_delivery_in_response(self) -> None:
        delivery = self.response_content["delivery"]
        self.assertEqual(delivery["type"], self.order_data["delivery"]["type"])
        self.assertEqual(delivery["status"], Delivery.Status.PROCESSING)

    def test_payment_in_response(self) -> None:
        payment = self.response_content["payment"]
        self.assertEqual(payment["type"], self.order_data["payment"]["type"])
        self.assertEqual(payment["is_paid"], True)

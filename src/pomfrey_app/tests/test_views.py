import json
from typing import override

from django.urls import reverse
from django.contrib.auth.password_validation import (
    MinimumLengthValidator, CommonPasswordValidator, NumericPasswordValidator
)
from rest_framework import status
from rest_framework.response import Response

from utils import (
    BaseRegistryTest,
    BaseAuthTest,
    BaseTestWithCreatedCustomer,
    BaseTestWithAuthenticationHeader,
    BaseLogoutTest,
    BaseViewTest,
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


class TestRegistry(BaseRegistryViewTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("registry")

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


class TestLogin(BaseAuthTest, BaseViewTest):
    @override
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.customer = cls.create_customer(cls.customer_data)
        cls.url = reverse("login")

    @override  # TODO: remove this
    def setUp(self) -> None:
        pass

    def test_returns_200_on_succeed(self) -> None:
        response = self.client.post(self.url, self.customer_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_user_with_token(self) -> None:
        response = self.client.post(self.url, self.customer_data)
        response_content = self._convert_response_to_json(response)
        self.assertEqual(response_content["email"], self.customer_data["email"])
        self.assertTrue(response_content["token"])


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


class TestOrderView(BaseOrderTest, BaseViewTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("order")

    @property
    def json_order_data(self) -> str:
        json_order_data = json.dumps(self.order_data)
        return json_order_data

    def test_returns_201_CREATED_on_success(self) -> None:
        response = self._send_post_request()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_check_response_content(self) -> None:
        content = self._get_response_content()

    def _get_response_content(self) -> dict:
        response = self._send_post_request()
        response_content = self._convert_response_to_json(response)
        return response_content

    def _send_post_request(self) -> Response:
        response = self.client.post(
            self.url,
            data=self.json_order_data,
            content_type="application/json"
        )
        return response

    def _check_order_id_in_response(self) -> None:
        content = self._get_response_content()
        self.assertTrue(content.get("id"))

    def test_customer_in_response(self) -> None:
        content = self._get_response_content()
        customer = content["customer"]

        self.assertEqual(customer["id"], self.order_data["order"]["customer"])
        self.assertEqual(customer["email"], self.customer_data["email"])

    def test_status_in_response(self) -> None:
        content = self._get_response_content()
        self.assertEqual(content["status"], Order.Status.PENDING)

    def test_pharmacy_in_response(self) -> None:
        content = self._get_response_content()
        pharmacy = content["pharmacy"]
        address = ", ".join(pharmacy["address"].values())

        self.assertEqual(pharmacy["phone"], self.pharmacy.phone)
        self.assertEqual(address, self.pharmacy.address.full_address)

    def test_delivery_in_response(self) -> None:
        content = self._get_response_content()
        delivery = content["delivery"]

        self.assertEqual(delivery["type"], self.order_data["delivery"]["type"])
        self.assertEqual(delivery["status"], Delivery.Status.PROCESSING)

    def test_payment_in_response(self) -> None:
        content = self._get_response_content()
        payment = content["payment"]

        self.assertEqual(payment["type"], self.order_data["payment"]["type"])
        self.assertEqual(payment["is_paid"], True)

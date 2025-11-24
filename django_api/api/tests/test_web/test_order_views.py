import json
from typing import override

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from logger.setup import LoggingConfig
from utils import BaseOrderTest, BaseViewTest
from api.data.order_data import Order, Delivery


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

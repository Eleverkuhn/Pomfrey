import json
from typing import override

from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response

from logger.setup import LoggingConfig
from utils import BaseOrderTest, BaseViewTest


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

    def test_returns_order_info(self) -> None:
        response = self._send_post_request()
        response_content = self._convert_response_to_json(response)
        LoggingConfig().logger.debug(f"Response: {response_content}")
        self.assertEqual(
            self.order_data["order"]["customer"], response_content["customer"]
        )
        self.assertEqual(
            self.order_data["order"]["pharmacy"], response_content["pharmacy"]
        )
        self.assertEqual(
            self.order_data["products"], response_content["products"]
        )

    def _send_post_request(self) -> Response:
        response = self.client.post(
            self.url,
            data=self.json_order_data,
            content_type="application/json"
        )
        return response

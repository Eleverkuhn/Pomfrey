from typing import override

from django.urls import reverse
from rest_framework import status

from logger.setup import LoggingConfig
from utils import BaseOrderTest, BaseViewTest


class TestOrderView(BaseOrderTest, BaseViewTest):
    @override
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("order")

    def test_returns_201_CREATED_on_success(self) -> None:
        response = self.client.post(self.url, data=self.order_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_returns_order_info(self) -> None:
        response = self.client.post(self.url, data=self.order_data)
        response_content = self._convert_response_to_json(response)
        LoggingConfig().logger.debug(f"Response: {response_content}")
        self.assertEqual(
            self.order_data.get("customer"), response_content.get("customer")
        )
        self.assertEqual(
            self.order_data.get("pharmacy"), response_content.get("pharmacy")
        )
        self.assertEqual(
            self.order_data.get("products"), response_content.get("products")
        )

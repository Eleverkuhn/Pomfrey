from django.urls import reverse

from utils import BaseRegistryTest
from api.data.customer_data import Customer


class TestRegistry(BaseRegistryTest):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse("registry")

    def test_returns_201_created_on_success(self) -> None:
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)

    def test_creates_customer(self) -> None:
        self.client.post(self.url, data=self.data)
        customer_db = Customer.objects.get(email=self.data.get("email"))
        self.assertTrue(customer_db)

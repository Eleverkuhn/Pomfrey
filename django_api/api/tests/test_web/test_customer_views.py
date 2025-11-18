from django.test import TestCase
from django.urls import reverse

from api.data.customer_data import Customer


class TestRegistry(TestCase):
    def setUp(self) -> None:
        self.post_data = {"email": "test@example.com", "password": "test"}
        self.url = reverse("registry")

    def test_returns_201_created_on_success(self) -> None:
        response = self.client.post(self.url, data=self.post_data)
        self.assertEqual(response.status_code, 201)

    def test_creates_customer(self) -> None:
        self.client.post(self.url, data=self.post_data)
        customer_db = Customer.objects.get(email=self.post_data.get("email"))
        self.assertTrue(customer_db)

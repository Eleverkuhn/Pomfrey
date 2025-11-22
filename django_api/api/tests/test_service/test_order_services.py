from typing import override

from utils import BaseTestService, BaseOrderTest
from api.service.order_services import OrderService
from api.data.order_data import Order, Delivery


class TestOrderService(BaseTestService, BaseOrderTest):
    service_class = OrderService

    @override
    def setUp(self) -> None:
        super().setUp()
        self.service = self.service_class(self.order_data)
        self.expected_delivery_output = {
            "type": self.order_data["delivery"]["type"],
            "status": Delivery.Status.PROCESSING
        }

    def test_creates_order(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        self.assertTrue(order_db)

    def test_created_order_contains_product_relations(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        products = zip(self.order_data["products"], order_db.products.all())
        for product_id, product_db in products:
            self.assertEqual(product_id, product_db.id)

    def test_created_order_contains_customer_relation(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        self.assertEqual(order_db.customer.email, self.data["email"])

    def test_created_order_contains_delivery_relation(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        self.assertEqual(
            order_db.delivery.type,
            self.expected_delivery_output["type"]
        )
        self.assertEqual(
            order_db.delivery.status,
            self.expected_delivery_output["status"]
        )

    def test_created_order_contains_payment_relation(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        self.assertEqual(
            order_db.payment.type, self.order_data["payment"]["type"],
        )
        self.assertEqual(
            order_db.payment.is_paid, self.order_data["payment"]["is_paid"]
        )

    def _execute_service_and_get_order_from_db(self):
        order = self.service.exec()
        order_db = Order.objects.get(id=order["id"])
        return order_db

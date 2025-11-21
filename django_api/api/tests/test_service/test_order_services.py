from typing import override

from utils import BaseTestService, BaseOrderTest
from api.service.order_services import OrderService
from api.data.order_data import Order


class TestOrderService(BaseTestService, BaseOrderTest):
    service_class = OrderService

    @override
    def setUp(self) -> None:
        super().setUp()
        self.service = self.service_class(self.order_data)

    def test_creates_order(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        self.assertTrue(order_db)

    def test_relations_created_correctly(self) -> None:
        order_db = self._execute_service_and_get_order_from_db()
        products = zip(self.order_data["products"], order_db.products.all())
        for product_id, product_db in products:
            self.assertEqual(product_id, product_db.id)

    def _execute_service_and_get_order_from_db(self):
        order = self.service.exec()
        order_db = Order.objects.get(id=order["id"])
        return order_db

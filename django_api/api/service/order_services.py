from logger.setup import OrderLogging
from api.web.serializers.order_serializers import (
    OrderSerializerInput, OrderSerializerOutput
)
from api.service.base_services import BaseService
from api.data.order_data import Order, OrderRepository


class OrderService(BaseService):
    serializer_class = OrderSerializerInput

    def exec(self) -> dict:
        validated_data = self.validate()
        order = self.create_order(validated_data)
        response_content = self._construct_response_content(order)
        return response_content

    def create_order(self, order_data: dict) -> Order:
        order = OrderRepository(order_data).create()
        OrderLogging(order.id, order.products.all()).create_log()
        return order

    def _construct_response_content(self, order: Order) -> dict:
        serializer = OrderSerializerOutput(instance=order)
        return serializer.data

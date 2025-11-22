from logger.setup import OrderLogging
from api.web.serializers.order_serializers import (
    OrderSerializerInput, OrderSerializerOutput
)
from api.service.base_services import BaseService
from api.data.order_data import Order, Delivery, Payment


class OrderService(BaseService):
    serializer_class = OrderSerializerInput

    def exec(self) -> dict:
        OrderLogging().logger.debug(f"Request Data: {self.request_data}")
        validated_data = self.validate()
        OrderLogging().logger.debug(f"Validated Data: {validated_data}")
        order = self.create_order(validated_data)
        response_content = self._construct_response_content(order)
        return response_content

    def create_order(self, order_data: dict) -> Order:
        order = self._create_order_in_db(order_data)
        OrderLogging(order.id, order.products.all()).create_log()
        return order

    def _create_order_in_db(self, order_data: dict) -> Order:
        products_data = order_data.pop("products")
        delivery_data = order_data.pop("delivery")
        payment_data = order_data.pop("payment")
        order = Order(**order_data)
        order.save()
        self._create_delivery_in_db(delivery_data, order)
        self._create_payment_in_db(payment_data, order)
        order.products.set(products_data)
        return order

    def _create_delivery_in_db(self, delivery_data: dict, order: Order) -> None:
        delivery = Delivery(**delivery_data, order=order)
        delivery.save()

    def _create_payment_in_db(self, payment_data: dict, order: Order) -> None:
        payment = Payment(**payment_data, order=order)
        payment.save()

    def _construct_response_content(self, order: Order) -> dict:
        OrderLogging().logger.debug(f"Order: {order}")
        serializer = OrderSerializerOutput(instance=order)
        OrderLogging().logger.debug(f"Serialized order: {serializer.data}")
        return serializer.data

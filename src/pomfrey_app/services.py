from django.contrib.auth import authenticate
from rest_framework.serializers import Serializer
from knox.models import AuthToken

from logger.setup import RegistryLogging, LoginLogging, OrderLogging
from pomfrey_app.serializers import (
    RegistrySerializer,
    CustomerSerializer,
    LoginSeralizer,
    OrderSerializerInput,
    OrderSerializerOutput
)
from pomfrey_app.models import Customer, Order
from pomfrey_app.model_repositories import OrderRepository


class BaseService:
    serializer_class: type[Serializer]

    def __init__(self, request_data: dict) -> None:
        self.request_data = request_data

    @property
    def serializer(self):
        return self.serializer_class(data=self.request_data)

    def validate(self) -> dict:
        serializer = self.serializer
        if serializer.is_valid(raise_exception=True):
            return serializer.validated_data


class RegistryService(BaseService):
    serializer_class = RegistrySerializer

    def exec(self) -> None:
        validated_data = self.validate()
        CustomerSerializer().create(validated_data)
        RegistryLogging(validated_data["email"]).create_log()


class LoginService(BaseService):
    serializer_class = LoginSeralizer

    def exec(self) -> dict:
        response_data = self._construct_response_data()
        LoginLogging(response_data["email"]).create_log()
        return response_data

    def _construct_response_data(self) -> dict:
        email, token = self._get_response_data()
        response_data = {"email": email, "token": token}
        return response_data

    def _get_response_data(self) -> tuple[str, str]:
        customer = self._get_customer()
        token = self._create_token(customer)
        return customer.email, token

    def _get_customer(self) -> Customer:
        validated_data = self.validate()
        customer = authenticate(
            email=validated_data.get("email"),
            password=validated_data.get("password")
        )
        return customer

    def _create_token(self, customer: Customer) -> AuthToken:
        token = AuthToken.objects.create(customer)[1]
        return token


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

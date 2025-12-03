from django.contrib.auth import authenticate
from knox.models import AuthToken

from logger.setup import RegistryLogging, LoginLogging
from api.web.serializers.customer_serializers import (
    RegistrySerializer, CustomerSerializer, LoginSeralizer
)
from api.data.customer_data import Customer
from api.service.base_services import BaseService


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

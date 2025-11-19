from rest_framework.serializers import ValidationError
from knox.models import AuthToken

from logger.setup import LoggingConfig
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
        self._log_created_user(validated_data.get("email"))

    def _log_created_user(self, email: str) -> None:
        LoggingConfig().logger.info(
            f"User {email} has been successfully created"
        )


class LoginService(BaseService):
    serializer_class = LoginSeralizer

    def exec(self) -> dict:
        response_data = self._construct_response_data()
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
        LoggingConfig().logger.debug(validated_data)
        customer = CustomerService(**validated_data).get()
        return customer

    def _create_token(self, customer: Customer) -> AuthToken:
        token = AuthToken.objects.create(customer)[1]
        return token


class CustomerService:
    def __init__(self, email: str, password: str) -> None:
        self.email = email
        self.password = password

    def get(self) -> Customer:
        customer = self._check_customer_exists(self.email)
        self._check_customer_password(customer, self.password)
        return customer

    def _check_customer_exists(self, email: str) -> Customer:
        try:
            customer = Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            raise ValidationError({"email": "User does not exist"})
        return customer

    def _check_customer_password(
            self, customer: Customer, password: str
    ) -> None:
        if not customer.check_password(password):
            raise ValidationError({"password": "Invalid password"})

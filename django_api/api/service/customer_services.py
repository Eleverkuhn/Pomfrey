from rest_framework.serializers import Serializer

from logger.setup import LoggingConfig
from api.web.serializers.customer_serializers import (
    RegistrySerializer, CustomerSerializer
)


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
        self._log_created_user(validated_data.get("email"))

    def _log_created_user(self, email: str) -> None:
        LoggingConfig().logger.info(
            f"User {email} has been successfully created"
        )


class LoginService:
    pass

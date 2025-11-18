from logger.setup import LoggingConfig
from api.web.serializers.customer_serializers import (
    RegistrySerializer, CustomerSerializer
)


class RegistryService:
    def __init__(self, request_data: dict) -> None:
        self.registry_data = request_data
        self.serializer = RegistrySerializer(data=self.registry_data)

    def exec(self) -> None:
        validated_data = self.validate()
        CustomerSerializer().create(validated_data)
        self._log_created_user(validated_data.get("email"))

    def validate(self) -> dict:
        if self.serializer.is_valid(raise_exception=True):
            return self.serializer.validated_data

    def _log_created_user(self, email: str) -> None:
        LoggingConfig().logger.info(
            f"User {email} has been successfully created"
        )

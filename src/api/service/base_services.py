from rest_framework.serializers import Serializer


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

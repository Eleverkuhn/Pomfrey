from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from api.data.customer_data import Customer


class PasswordMatchesValidator:
    requires_context = True

    def __init__(self, password_field: str) -> None:
        self.password_field = password_field

    def __call__(self, value: str, confirm_password_field) -> None:
        password = confirm_password_field.parent.initial_data.get(
            self.password_field
        )
        if not self._compare_passwords(password, value):
            self._raise_validation_err()

    def _compare_passwords(
            self, base_password: str, password_to_compare: str
    ) -> bool:
        return base_password == password_to_compare

    def _raise_validation_err(self) -> None:
        message = "Passwords don't match"
        raise ValidationError(message)


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Customer
        fields = ["id", "email", "password"]

    def create(self, validated_data: dict) -> Customer:
        validated_data.pop("confirm_password")
        password = validated_data.pop("password")
        customer = Customer.objects.create_user(
            **validated_data, password=password
        )
        return customer


class RegistrySerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(Customer.objects.all())]
    )
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[PasswordMatchesValidator("password")]
    )

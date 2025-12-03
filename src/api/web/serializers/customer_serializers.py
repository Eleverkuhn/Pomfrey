from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from logger.setup import LoggingConfig
from api.data.customer_data import Customer


class BuiltInPasswordValidator:
    def __call__(self, value) -> None:
        validate_password(value)


class PasswordMatchesValidator:
    requires_context = True

    def __init__(self, password_field: str) -> None:
        self.password_field = password_field

    def __call__(self, value: str, confirm_password_field) -> None:
        password = confirm_password_field.parent.initial_data.get(
            self.password_field
        )
        LoggingConfig().logger.debug(password)
        if not self.compare_passwords(password, value):
            self.raise_validation_err()

    def compare_passwords(
            self, base_password: str, password_to_compare: str
    ) -> bool:
        return base_password == password_to_compare

    def raise_validation_err(self) -> None:
        raise ValidationError(self.get_error_message())

    def get_error_message(self) -> str:
        error_message = "Passwords do not match"
        return error_message


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


class CustomerOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "email"]


class LoginSeralizer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class RegistrySerializer(LoginSeralizer):
    email = serializers.EmailField(
        validators=[UniqueValidator(Customer.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        validators=[BuiltInPasswordValidator()]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[PasswordMatchesValidator("password")]
    )

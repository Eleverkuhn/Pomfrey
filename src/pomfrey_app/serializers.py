from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, ValidationError

from logger.setup import LoggingConfig
from pomfrey_app.models import (
    Customer,
    Address,
    Pharmacy,
    Delivery,
    Payment,
    Order
)


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


class AddressSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["id"]


class PharmacySerializerOutput(serializers.ModelSerializer):
    address = AddressSerializerOutput()

    class Meta:
        model = Pharmacy
        exclude = ["id"]


class DeliverySeriazlierInput(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ["type"]


class DeliverySeriazlierOutput(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ["type", "status"]


class PaymentSerializer(serializers.ModelSerializer):
    """
    This serializer is applied both for input and output validation
    """
    class Meta:
        model = Payment
        fields = ["type", "is_paid"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["customer", "pharmacy"]


class OrderSerializerInput(serializers.ModelSerializer):
    delivery = DeliverySeriazlierInput()
    payment = PaymentSerializer()
    order = OrderSerializer()

    class Meta:
        model = Order
        fields = ["order", "products", "delivery", "payment"]


class OrderSerializerOutput(serializers.ModelSerializer):
    customer = CustomerOutputSerializer()
    pharmacy = PharmacySerializerOutput()
    delivery = DeliverySeriazlierOutput()
    payment = PaymentSerializer()

    class Meta:
        model = Order
        fields = "__all__"

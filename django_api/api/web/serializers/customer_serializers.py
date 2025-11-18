from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.data.customer_data import Customer


class CustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Customer
        fields = ["id", "email", "password"]

    def create(self, validated_data: dict) -> Customer:
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

from rest_framework import serializers

from api.data.order_data import Order


class OrderSerializerInput(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["customer", "products", "pharmacy"]


class OrderSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

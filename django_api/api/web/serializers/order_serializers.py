from rest_framework import serializers

from api.data.order_data import Order, Delivery, Payment


class DeliverySeriazlierInput(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = ["type", "status"]


class DeliverySeriazlierOutput(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"


class PaymentSerializerInput(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["type", "is_paid"]


class PamentSeriazlierOutput(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["customer", "pharmacy"]


class OrderSerializerInput(serializers.ModelSerializer):
    delivery = DeliverySeriazlierInput()
    payment = PaymentSerializerInput()
    order = OrderSerializer()

    class Meta:
        model = Order
        fields = ["order", "products", "delivery", "payment"]


class OrderSerializerOutput(serializers.ModelSerializer):
    delivery = DeliverySeriazlierOutput()

    class Meta:
        model = Order
        fields = "__all__"

from rest_framework import serializers

from api.data.geo_data import Address


class AddressSerializerOutput(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["id"]

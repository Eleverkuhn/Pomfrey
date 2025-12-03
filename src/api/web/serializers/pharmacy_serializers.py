from rest_framework import serializers

from api.web.serializers.geo_serializers import AddressSerializerOutput
from api.data.pharmacy_data import Pharmacy


class PharmacySerializerOutput(serializers.ModelSerializer):
    address = AddressSerializerOutput()

    class Meta:
        model = Pharmacy
        exclude = ["id"]

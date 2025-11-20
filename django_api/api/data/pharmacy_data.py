from django.db import models

from api.data.base_data import FieldDefault


class PharmacyAddress(models.Model):
    region = models.CharField(max_length=FieldDefault.geo_title_length)
    city = models.CharField(max_length=FieldDefault.geo_title_length)
    street = models.CharField(max_length=FieldDefault.street_length)
    apartment = models.CharField(max_length=FieldDefault.apartment_length)
    postal_code = models.CharField(max_length=FieldDefault.postal_code_length)

    class Meta:
        db_table = "pharmacy_addresses"


class PharmacyWorkingSchedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = "pharmacy_working_schedules"


class Pharmacy(models.Model):
    address = models.ForeignKey(PharmacyAddress, on_delete=models.CASCADE)
    schedule = models.ForeignKey(
        PharmacyWorkingSchedule, on_delete=models.CASCADE
    )

    class Meta:
        db_table = "pharmacies"

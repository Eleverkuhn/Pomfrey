from typing import override

from django.db import models

from api.data.customer_data import Customer
from api.data.product_data import Product
from api.data.pharmacy_data import Pharmacy


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)

    @override
    def __repr__(self) -> str:
        repr = f"{self.id} {self.customer} ({self.products.all()})"
        return repr

    class Meta:
        db_table = "orders"

from django.db import models

from api.data.base_data import ModelAbstract
from api.data.customer_data import Customer
from api.data.product_data import Product
from api.data.pharmacy_data import Pharmacy


class Order(ModelAbstract):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    pharmacy = models.ForeignKey(Pharmacy, on_delete=models.CASCADE)

    class Meta:
        db_table = "orders"

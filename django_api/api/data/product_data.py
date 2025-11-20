from django.db import models

from api.data.base_data import FieldDefault


class ProductAbstract(models.Model):
    title = models.CharField(max_length=FieldDefault.title_lenght)

    class Meta:
        abstract = True


class ProductCategory(ProductAbstract):
    pass

    class Meta:
        db_table = "product_categoires"


class ProductType(ProductAbstract):
    pass

    class Meta:
        db_table = "product_types"


class Product(ProductAbstract):
    price = models.DecimalField(
        max_digits=FieldDefault.decimal_digits,
        decimal_places=FieldDefault.decimal_places
    )
    amount = models.IntegerField()

    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    categories = models.ManyToManyField(ProductCategory)

    class Meeta:
        db_table = "products"

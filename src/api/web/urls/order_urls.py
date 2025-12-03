from django.urls import path

from api.web.views.order_views import OrderView

urlpatterns = [
    path("", OrderView.as_view(), name="order"),
]

from django.urls import path

from pomfrey_app.views import OrderView

urlpatterns = [
    path("", OrderView.as_view(), name="order"),
]

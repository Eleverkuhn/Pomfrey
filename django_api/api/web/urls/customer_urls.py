from django.urls import path

from api.web.views.customer_views import CustomerPage

urlpatterns = [
    path("", CustomerPage.as_view(), name="my"),
]

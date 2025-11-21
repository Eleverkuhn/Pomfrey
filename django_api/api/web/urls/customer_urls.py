from django.urls import path

from api.web.views.customer_views import CustomerPageView

urlpatterns = [
    path("", CustomerPageView.as_view(), name="my"),
]

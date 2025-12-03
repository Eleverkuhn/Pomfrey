from django.urls import path

from pomfrey_app.views import CustomerPageView

urlpatterns = [
    path("", CustomerPageView.as_view(), name="my"),
]

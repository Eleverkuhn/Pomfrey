from django.urls import path

from api.web.views.customer_views import Registry

urlpatterns = [
    path("registry/", Registry.as_view(), name="registry"),
]

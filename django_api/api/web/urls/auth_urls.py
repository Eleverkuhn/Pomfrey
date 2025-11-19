from django.urls import path

from api.web.views.customer_views import Registry, Login

urlpatterns = [
    path("registry/", Registry.as_view(), name="registry"),
    path("login/", Login.as_view(), name="login"),
]

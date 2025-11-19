from django.urls import path
from knox.views import LogoutView, LogoutAllView

from api.web.views.customer_views import Registry, Login

urlpatterns = [
    path("registry/", Registry.as_view(), name="registry"),
    path("login/", Login.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("logoutall/", LogoutAllView.as_view(), name="logout_all"),
]

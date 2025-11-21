from django.contrib import admin
from django.urls import path, include

from api.web.views.main_view import MainView

urlpatterns = [
    path("", MainView.as_view()),
    path("admin/", admin.site.urls),
    path("auth/", include("api.web.urls.auth_urls")),
    path("my/", include("api.web.urls.customer_urls")),
    path("orders/", include("api.web.urls.order_urls")),
]

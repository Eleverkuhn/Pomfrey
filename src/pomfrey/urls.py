from django.contrib import admin
from django.urls import path, include

from pomfrey_app.views import MainView

urlpatterns = [
    path("", MainView.as_view()),
    path("admin/", admin.site.urls),
    path("auth/", include("pomfrey_app.urls.auth_urls")),
    path("my/", include("pomfrey_app.urls.customer_urls")),
    path("orders/", include("pomfrey_app.urls.order_urls")),
]

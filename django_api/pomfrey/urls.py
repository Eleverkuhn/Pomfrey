from django.contrib import admin
from django.urls import path, include

from api.web.views.main_view import Main

urlpatterns = [
    path("", Main.as_view()),
    path("admin/", admin.site.urls),
    path("auth/", include("api.web.urls.auth_urls")),
    path("auth/", include("knox.urls")),
    path("my/", include("api.web.urls.customer_urls")),
]

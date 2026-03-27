from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.login_personalizado.urls")), 
    path("", include("apps.Roles_grupos.urls")),
]

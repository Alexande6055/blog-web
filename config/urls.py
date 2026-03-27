from django.urls import include, path

urlpatterns = [
    #    path("admin/", admin.site.urls),
    path("", include("apps.departamento_sucursal.urls")),  # Para login/logout
    path("", include("apps.login_personalizado.urls")),  # Para login/logout
    path("", include("apps.Roles_grupos.urls")),  #
    path("", include("apps.directorios.urls")),  #
]

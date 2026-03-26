from django.urls import path
from .views.roles_view import BuscarRolesView
from .views.role_form_view import RolFormView
from .views.roles_page_view import RolesHomeView

app_name = "roles_grupos"

urlpatterns = [
    path("", RolesHomeView.as_view(), name="home"),
    path("buscar-roles/", BuscarRolesView.as_view(), name="buscar_roles"),
    path("rol/formulario/", RolFormView.as_view(), name="rol_formulario"),
    path(
        "rol/formulario/<int:rol_id>/",
        RolFormView.as_view(),
        name="rol_formulario_edit",
    ),
    path("editar/<int:edit_id>/", RolesHomeView.as_view(), name="home_edit"),
]

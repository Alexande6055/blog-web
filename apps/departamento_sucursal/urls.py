from django.urls import path
from .views import crear_departamento_view
from .views import crear_sucursal_view

urlpatterns = [
    path(
        "departamento/crear/",
        crear_departamento_view.crear_departamento_view,
        name="crear_departamento",
    ),
    path(
        "sucursal/crear/",
        crear_sucursal_view.crear_sucursal_view,
        name="crear_sucursal",
    ),
]

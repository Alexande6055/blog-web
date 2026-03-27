from django.urls import path
from .view import  list_directorios,crear_carpeta_view,ver_archivos_view


urlpatterns = [
    path("directorios/", list_directorios.directorios_view, name="directorios"),
        path("carpeta/<int:carpeta_id>/", ver_archivos_view.ver_archivos_view, name="carpeta"),
    path("carpeta/crear/", crear_carpeta_view.crear_carpeta_view, name="crear_carpeta"),
]

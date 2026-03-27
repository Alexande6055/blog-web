from django.db.models import Count
from apps.archivo.models import  Archivo
from apps.directorios.models import Carpeta
def obtener_carpetas_con_conteo(padre_id=None):
    """
    Si padre_id es None, trae las raíces.
    Si padre_id tiene un valor, trae las subcarpetas de esa carpeta.
    """
    queryset = Carpeta.objects.filter(activo=True, padre_id=padre_id)

    return queryset.annotate(
        total_archivos=Count("archivos", distinct=True),
        total_subcarpetas=Count("subcarpetas", distinct=True),
    ).select_related("departamento_sucursal", "padre")


def obtener_ruta_breadcrumbs(carpeta_id):
    """
    Retorna una lista de carpetas desde la raíz hasta la actual.
    Útil para la navegación en el frontend.
    """
    ruta = []
    try:
        actual = Carpeta.objects.get(id=carpeta_id)
        while actual:
            ruta.insert(0, actual)  # Insertamos al inicio para mantener el orden
            actual = actual.padre
    except Carpeta.DoesNotExist:
        pass
    return ruta


def obtener_archivos_vigentes_por_carpeta(carpeta_id):
    """
    Retorna solo los archivos que el usuario debe ver (vigentes y activos).
    Optimizamos con select_related para evitar el problema N+1 al acceder a la carpeta o el tipo.
    """
    data = Archivo.objects.filter(
        id_carpeta_id=carpeta_id, es_version_vigente=True, activo=True
    ).select_related("id_tipo_documento", "id_usuario_subida")
    return data


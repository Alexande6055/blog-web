
from django.shortcuts import render
from apps.directorios.selectors.directorios import obtener_archivos_vigentes_por_carpeta, obtener_carpetas_con_conteo, obtener_ruta_breadcrumbs
from apps.departamento_sucursal.selectors import departamento,sucursal
def ver_archivos_view(request, carpeta_id):
    # 1. Traemos las subcarpetas (Nivel siguiente)
    subcarpetas = obtener_carpetas_con_conteo(padre_id=carpeta_id)

    # 2. Traemos los archivos de ESTA carpeta
    archivos = obtener_archivos_vigentes_por_carpeta(carpeta_id)

    # 3. Traemos la ruta para el Breadcrumb
    breadcrumbs = obtener_ruta_breadcrumbs(carpeta_id)

    # 4. Traemos las sucursales para el dropdown al crear carpeta dentro de esta carpeta
    sucursales = sucursal.obtener_sucursales_listar()
    # 5. Traemos los departamentos para el dropdown al crear carpeta dentro de esta carpeta
    departamentos = departamento.obtener_departamentos_listar()
    contexto = {
        "lista_carpetas": subcarpetas,
        "lista_archivos": archivos,
        "breadcrumbs": breadcrumbs,
        "carpeta_actual_id": carpeta_id,
        "lista_sucursales": sucursales,
        "lista_departamentos": departamentos,
    }
    return render(request, "posts/directorios.html", contexto)


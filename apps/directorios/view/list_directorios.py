from django.shortcuts import render
from apps.directorios.selectors.directorios import obtener_carpetas_con_conteo
from apps.departamento_sucursal.selectors.departamento import obtener_departamentos_listar
from apps.departamento_sucursal.selectors.sucursal import obtener_sucursales_listar




def directorios_view(request):
    # Aquí podrías usar un selector para traer solo las carpetas activas, por ejemplo
    carpetas = obtener_carpetas_con_conteo()
    sucursales = obtener_sucursales_listar()
    departamentos = obtener_departamentos_listar()
    contexto = {
        "lista_carpetas": carpetas,
        "lista_sucursales": sucursales,
        "lista_departamentos": departamentos,
    }
    return render(request, "pages/index.html", contexto)

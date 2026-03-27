from django.shortcuts import redirect
from apps.directorios.services.directorios import crear_carpeta
from django.contrib import messages
from apps.departamento_sucursal.modelos import Sucursal

def crear_carpeta_view(request):

    if request.method == "POST":
        nombre = request.POST.get("nombre_carpeta")
        padre_id = request.POST.get("carpeta_id")
        sucursal_id = request.POST.get("sucursal_id")
        departamento_id = request.POST.get("departamento_id")
        if not padre_id:
            padre_id = None
        # Validaciones básicas
        if not nombre or not sucursal_id or not departamento_id:
            messages.error(
                request, "El nombre, la sucursal y el departamento son obligatorios."
            )
            return redirect(request.META.get("HTTP_REFERER"))

        try:
            carpeta = crear_carpeta(
                nombre=nombre,
                id_usuario_creacion=request.user.id,
                id_sucursal=sucursal_id,
                id_departamento=departamento_id,
                id_carpeta_padre=padre_id,
            )
            messages.success(request, f"Carpeta '{nombre}' creada con éxito.")

        except Sucursal.DoesNotExist:
            messages.error(request, "La sucursal seleccionada no es válida.")
        except Exception as e:
            messages.error(request, f"Error al crear la carpeta: {e}")

    # Regresamos a la página donde estaba el usuario
    return redirect(request.META.get("HTTP_REFERER"))

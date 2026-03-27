from django.shortcuts import  redirect
from apps.departamento_sucursal.modelos import  Sucursal  # Importante
from django.contrib import messages


def crear_sucursal_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        direccion = request.POST.get("direccion")
        telefono = request.POST.get("telefono")

        if nombre:
            try:
                Sucursal.objects.create(
                    nombre=nombre, direccion=direccion, telefono=telefono
                )
                messages.success(request, f"Sucursal '{nombre}' creada correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear la sucursal: {e}")
        else:
            messages.error(request, "El nombre de la sucursal es obligatorio.")

    # Redirigir a la página desde la que vino el usuario
    return redirect(request.META.get("HTTP_REFERER", "home"))


from django.contrib import messages
from django.shortcuts import redirect
from apps.departamento_sucursal.modelos import Departamento


def crear_departamento_view(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")

        if nombre:
            try:
                Departamento.objects.create(nombre=nombre, descripcion=descripcion)
                messages.success(
                    request, f"Departamento '{nombre}' creado correctamente."
                )
            except Exception as e:
                messages.error(request, f"Error al crear el departamento: {e}")
        else:
            messages.error(request, "El nombre del departamento es obligatorio.")

    # Redirigir a la página desde la que vino el usuario
    return redirect(request.META.get("HTTP_REFERER", "home"))

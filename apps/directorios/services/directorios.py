from django.contrib.auth import get_user_model
from apps.departamento_sucursal.modelos import  Departamento, Sucursal
from apps.directorios.models import Carpeta
from django.db import transaction
User = get_user_model()  # Esto detectará automáticamente tu modelo personalizado


def crear_carpeta(
    nombre, id_usuario_creacion, id_sucursal, id_departamento, id_carpeta_padre=None
):
   with transaction.atomic():  # Si algo falla adentro, no se guarda nada en la BD
     # 1. Obtener instancias (usamos .get() porque el ID viene validado de la vista)
    sucursal = Sucursal.objects.get(id=id_sucursal)
    departamento = Departamento.objects.get(id=id_departamento)
    usuario = User.objects.get(id=id_usuario_creacion)

    # 2. Manejar el padre (si viene cadena vacía del form, lo tratamos como None)
    padre = None
    if id_carpeta_padre and str(id_carpeta_padre).strip():
        padre = Carpeta.objects.get(id=id_carpeta_padre)

    # 3. Crear y retornar
    return Carpeta.objects.create(
        nombre=nombre,
        nombre_nas=nombre.strip().replace(" ", "_"),
        creado_por=usuario,  # Aquí se asigna tu modelo User personalizado
        departamento=departamento,
        sucursal=sucursal,
        padre=padre,
    )

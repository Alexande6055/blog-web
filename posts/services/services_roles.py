from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

def update_rol(rol_id, nuevo_nombre, permisos_ids):
    """
    Actualiza un rol (Group) con nuevo nombre y conjunto de permisos.
    
    Args:
        rol_id (int): ID del grupo a actualizar.
        nuevo_nombre (str): Nuevo nombre para el grupo.
        permisos_ids (list[int]): Lista de IDs de permisos que deben quedar asignados.
    
    Returns:
        Group: El grupo actualizado.
    
    Raises:
        ObjectDoesNotExist: Si el grupo no existe.
        Exception: Si ocurre un error durante la transacción.
    """
    try:
        with transaction.atomic():
            # Obtener el grupo
            grupo = Group.objects.get(id=rol_id)
            
            # Actualizar nombre si es diferente (opcional)
            if nuevo_nombre and grupo.name != nuevo_nombre:
                grupo.name = nuevo_nombre
                grupo.save()
            
            # Obtener objetos Permission válidos
            permisos = Permission.objects.filter(id__in=permisos_ids)
            # Asignar permisos (reemplaza los existentes)
            grupo.permissions.set(permisos)
            
            return grupo
    except ObjectDoesNotExist:
        raise  # Re-lanzar para que la vista maneje el 404
    except Exception as e:
        # Podrías loguear el error y relanzar o manejar según tu política
        raise
    
def create_rol(nombre, permisos_ids):
    """
    Crea un nuevo rol (Group) con un nombre y conjunto de permisos.
    
    Args:
        nombre (str): Nombre para el nuevo grupo.
        permisos_ids (list[int]): Lista de IDs de permisos a asignar.
    
    Returns:
        Group: El grupo creado.
    
    Raises:
        Exception: Si ocurre un error durante la creación.
    """
    try:
        with transaction.atomic():
            # Crear el grupo
            grupo = Group.objects.create(name=nombre)
            
            # Obtener objetos Permission válidos
            permisos = Permission.objects.filter(id__in=permisos_ids)
            # Asignar permisos al nuevo grupo
            grupo.permissions.set(permisos)
            
            return grupo
    except Exception as e:
        # Podrías loguear el error y relanzar o manejar según tu política
        raise
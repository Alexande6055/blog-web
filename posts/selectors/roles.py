from django.contrib.auth.models import Group, Permission
from django.db.models import Count


def listar_roles():
    # Anotamos cada grupo con el conteo de su relación 'permissions'
    roles = Group.objects.annotate(total_permisos=Count("permissions"))
    return roles


def buscar_roles_por_nombre(nombre):
    # Buscar roles por nombre (case-insensitive)
    roles = Group.objects.filter(name__icontains=nombre)
    return roles


# def buscar_rol_por_id_con_permisos(rol_id):
# Buscar un rol por ID e incluir sus permisos relacionados
#    rol = Group.objects.prefetch_related('permissions').get(id=rol_id)
# Necesitamos un objeto de la siguiente forma
# el rol con sus permisos relacionados, y una lista de permisos disponibles para asignar
#    rol_con_permisos = {
#    rol:{
#     "id": rol.id,
#     "name": rol.name,
#     "permissions": list(rol.permissions.values("id", "name", "codename"))
#    },
#   permisosDisponibles: list(Permission.objects.values("id", "name", "codename"))
#
#    return rol


def obtener_rol_con_permisos(rol_id):
    """
    Retorna un diccionario con:
    - rol: datos del grupo y sus permisos asignados
    - permisos_disponibles: lista de todos los permisos (id, name)
    """
    rol = Group.objects.prefetch_related("permissions").get(id=rol_id)

    # Construir el diccionario con los datos del rol
    datos_rol = {
        "id": rol.id,
        "name": rol.name,
        "permissions": list(rol.permissions.values("id", "name", "codename")),
    }

    # Obtenemos los que NO están asociados a este rol directamente en la consulta
    permisos_disponibles = list(
        Permission.objects.exclude(group=rol).values("id", "name", "codename")
    )

    return {
        "rol": datos_rol,
        "permisos_disponibles": permisos_disponibles,
    }

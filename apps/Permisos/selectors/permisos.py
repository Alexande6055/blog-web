from django.contrib.auth.models import Group, Permission

def listar_permisos():
    """Si quieres ver todos los permisos disponibles en el sistema
    Importante: devolver una lista para que el template pueda incrustarlo en JS con `|safe`
    sin que aparezca el wrapper de QuerySet ("<QuerySet [...]>")."""
    return list(Permission.objects.all().values("id", "name", "codename"))


def listar_permisos_excluyendo(rol: Group):
    """Metodo para obtener lista de permisos excluyendo los permisos pasados por parametro"""
    return list(
        Permission.objects.exclude(
            id__in=rol.permissions.values_list("id", flat=True)
        ).values("id", "name", "codename")
    )

from django.contrib.auth.models import Permission


def listar_permisos():
    # Si quieres ver todos los permisos disponibles en el sistema
    # Importante: devolver una lista para que el template pueda incrustarlo en JS con `|safe`
    # sin que aparezca el wrapper de QuerySet ("<QuerySet [...]>").
    return list(Permission.objects.all().values('id', 'name', 'codename'))

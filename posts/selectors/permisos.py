from django.contrib.auth.models import Permission


def listar_permisos():
    # Si quieres ver todos los permisos disponibles en el sistema
    permisos = Permission.objects.all().values("id", "name", "codename")
    return permisos

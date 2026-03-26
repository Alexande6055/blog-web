from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction


def update_rol(rol_id, nuevo_nombre, permisos_ids):
    try:
        with transaction.atomic():
            grupo = Group.objects.get(id=rol_id)
            if nuevo_nombre and grupo.name != nuevo_nombre:
                grupo.name = nuevo_nombre
                grupo.save()

            permisos = Permission.objects.filter(id__in=permisos_ids)
            grupo.permissions.set(permisos)
            return grupo
    except ObjectDoesNotExist:
        raise
    except Exception:
        raise


def create_rol(nombre, permisos_ids):
    try:
        with transaction.atomic():
            grupo = Group.objects.create(name=nombre)
            permisos = Permission.objects.filter(id__in=permisos_ids)
            grupo.permissions.set(permisos)
            return grupo
    except Exception:
        raise

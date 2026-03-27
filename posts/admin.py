from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import (
    ExportMixin,
)  # Requiere: pip install django-import-export
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Departamento, Sucursal, Log, EventoLog
from django.contrib.auth import get_user_model 
User = get_user_model()
class LogResource(resources.ModelResource):
    # Traemos campos específicos de la relación EventoLog usando doble guion bajo
    evento_nombre = fields.Field(
        column_name="Nombre del Evento", attribute="evento__nombre"
    )
    evento_tipo = fields.Field(column_name="Tipo de Acción", attribute="evento__tipo")
    evento_modulo = fields.Field(
        column_name="Módulo del Sistema", attribute="evento__modulo"
    )

    class Meta:
        model = Log
        # Definimos el orden de las columnas en el Excel
        fields = (
            "fecha_hora",
            "user",
            "email",
            "ci",
            "evento_modulo",
            "evento_nombre",
            "evento_tipo",
            "resultado",
            "direccion_ip",
            "detalle",
        )
        export_order = fields


# 1. Configuración de Usuarios (Tu código mejorado)
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        "username",
        "email",
        "nombre_completo",
        "cargo",
        "is_staff",
        "is_active",
    ]
    list_filter = ["is_staff", "is_active", "departamento", "sucursal"]

    fieldsets = UserAdmin.fieldsets + (
        (
            "Información Extra",
            {"fields": ("nombre_completo", "ci", "cargo", "departamento", "sucursal")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Información Extra",
            {"fields": ("nombre_completo", "ci", "cargo", "departamento", "sucursal")},
        ),
    )


# 2. Configuración de Logs (SOLO LECTURA + EXPORTAR)
@admin.register(Log)
class LogAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = LogResource  # <--- AQUÍ VINCULAMOS EL TRADUCTOR
    # Qué columnas ver en la tabla principal
    list_display = ("fecha_hora", "usuario", "evento", "resultado", "direccion_ip")
    # Filtros laterales rápidos
    list_filter = ("resultado", "evento__modulo", "fecha_hora")
    # Buscador por texto
    search_fields = ("usuario", "email", "ci", "detalle")

    # --- SEGURIDAD: Bloqueamos edición y borrado ---
    def has_add_permission(self, request):
        return False  # Nadie puede crear logs a mano

    def has_change_permission(self, request, obj=None):
        return False  # Nadie puede editar un log (solo ver)

    def has_delete_permission(self, request, obj=None):
        return False  # Los logs son sagrados, no se borran

    # Hacemos que al entrar al detalle, todos los campos sean grises (bloqueados)
    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]


# 3. Catálogos Simples
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "direccion", "telefono")


# 4. Configuración de Eventos (Opcional verlo en admin)
@admin.register(EventoLog)
class EventoLogAdmin(admin.ModelAdmin):
    list_display = ("modulo", "nombre", "tipo")

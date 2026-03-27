from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import (
    ExportMixin,
)  # Requiere: pip install django-import-export
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import  Log, EventoLog
from django.contrib.auth import get_user_model
from apps.directorios.models import Carpeta, PermisoCarpeta
from apps.departamento_sucursal.modelos import Departamento, Sucursal
from apps.archivo.models import Archivo, TipoDocumento
User = get_user_model()


class PermisoCarpetaInline(admin.TabularInline):
    model = PermisoCarpeta
    extra = 1  # Te muestra una fila vacía para agregar rápido
    autocomplete_fields = [
        "usuario",
        "grupo",
    ]  # Para buscar rápido si tienes muchos usuarios


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
            "username",
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
    list_display = ('username', 'email', 'get_departamento', 'get_sucursal')
    list_filter = ()  # vacío o solo otros campos existentes

    def get_departamento(self, obj):
        return obj.departamento_sucursal.departamento.nombre if obj.departamento_sucursal else ''
    get_departamento.short_description = 'Departamento'

    def get_sucursal(self, obj):
        return obj.departamento_sucursal.sucursal.nombre if obj.departamento_sucursal else ''
    get_sucursal.short_description = 'Sucursal'

# 2. Configuración de Logs (SOLO LECTURA + EXPORTAR)
@admin.register(Log)
class LogAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = LogResource  # <--- AQUÍ VINCULAMOS EL TRADUCTOR
    # Qué columnas ver en la tabla principal
    list_display = ("fecha_hora", "usuario", "evento", "resultado", "direccion_ip")
    # Filtros laterales rápidos
    list_filter = ("resultado", "evento__modulo", "fecha_hora")
    # Buscador por texto
    search_fields = ("usuario__username", "email", "ci", "detalle")

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
    exclude = (
        "ruta_base_nas",
    )  # Ocultamos este campo en el admin para evitar confusiones
    list_display = ("nombre", "direccion", "telefono")


# 4. Configuración de Eventos (Opcional verlo en admin)
@admin.register(EventoLog)
class EventoLogAdmin(admin.ModelAdmin):
    list_display = ("modulo", "nombre", "tipo")


@admin.register(Carpeta)
class CarpetaAdmin(admin.ModelAdmin):
    inlines = [PermisoCarpetaInline]
    exclude = ("creado_por",)
    list_display = ("nombre", "get_sucursal", "get_departamento", "activo")
    search_fields = ("nombre",)

    def get_sucursal(self, obj):
        return obj.departamento_sucursal.sucursal.nombre if obj.departamento_sucursal else '--'
    get_sucursal.short_description = 'Sucursal'

    def get_departamento(self, obj):
        return obj.departamento_sucursal.departamento.nombre if obj.departamento_sucursal else '--'
    get_departamento.short_description = 'Departamento'

    
@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_original",
        "id_carpeta",
        "id_usuario_subida",
        "fecha_subida",
    )
    search_fields = ("nombre_original",)
    list_filter = ("fecha_subida", "id_usuario_subida")


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)

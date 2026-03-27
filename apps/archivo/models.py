from django.db import models
from django.conf import settings
import os
from django.utils import timezone

# ============================
# 3. TIPO DE DOCUMENTO
# ============================
class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    # Esquema de metadatos (JSON) para definir campos adicionales obligatorios/opcionales
    esquema_metadatos = models.JSONField(default=dict, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tipo de Documento"
        verbose_name_plural = "Tipos de Documento"

    def __str__(self):
        return self.nombre


# ============================
# 4. ARCHIVO (DOCUMENTO)
# ============================
class Archivo(models.Model):
    ESTADO_CHOICES = [
        ("BORRADOR", "Borrador (En edición)"),
        ("PENDIENTE", "Pendiente"),
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
        ("EN_CORRECCION", "En corrección"),
    ]

    # Datos del archivo
    nombre_original = models.CharField(max_length=255)
    nombre_archivo_nas = models.CharField(max_length=255, unique=True)
    tipo_mime = models.CharField(max_length=100, blank=True)  # application/pdf, etc.
    tamano = models.PositiveIntegerField(default=0)  # Tamaño en bytes

    # Metadatos obligatorios
    numero_operacion = models.CharField(max_length=200, db_index=True)
    numero_identificacion_socio = models.CharField(max_length=200, db_index=True)
    nombre_socio = models.CharField(max_length=255)

    # Metadatos dinámicos (JSON)
    metadatos = models.JSONField(default=dict, blank=True, null=True)

    # Relaciones
    id_usuario_subida = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # No se puede eliminar usuario que subió documentos
        related_name="documentos_subidos",
    )

    id_tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.PROTECT, related_name="documentos"
    )
    id_carpeta = models.ForeignKey(
        "directorios.Carpeta",
        on_delete=models.PROTECT,  # No borrar carpetas que tengan archivos
        related_name="archivos",
    )
    # Versionado
    id_documento_padre = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="historial_versiones",
    )
    version = models.PositiveIntegerField(default=1)
    # Este campo es el "Suiche" maestro para la interfaz
    es_version_vigente = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Si es True, este es el archivo que verán los usuarios normales.",
    )

    # Borrado lógico del archivo
    activo = models.BooleanField(default=True, db_index=True)
    # Estado y aprobación
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="BORRADOR", db_index=True
    )
    activo = models.BooleanField(default=True, db_index=True)  # Indica versión vigente

    # Bloqueo para edición
    bloqueado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_bloqueados",
    )
    fecha_bloqueo = models.DateTimeField(null=True, blank=True)

    # Aprobación
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    id_usuario_aprobacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_aprobados",
    )

    # Auditoría
    fecha_subida = models.DateTimeField(auto_now_add=True, db_index=True)
    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )  # Última modificación (cambio de estado, etc.)

    @property
    def obtener_ruta_completa_nas(self):
        """Retorna la ubicación exacta del archivo para que el sistema lo encuentre."""
        return os.path.join(
            self.id_carpeta.ruta_fisica_completa, self.nombre_archivo_nas
        )

    def esta_visible_en_sistema(self):
        """El archivo solo es visible si él está activo Y su carpeta también."""
        return self.activo and self.id_carpeta.esta_visible()

    class Meta:
        verbose_name = "Archivo"
        verbose_name_plural = "Archivos"
        indexes = [
            models.Index(fields=["numero_identificacion_socio", "numero_operacion"]),
            models.Index(fields=["estado", "activo"]),
            models.Index(fields=["fecha_subida"]),
            # Índice GIN para metadatos (PostgreSQL)
            models.Index(
                name="archivo_metadatos_gin",
                fields=["metadatos"],
                condition=models.Q(metadatos__isnull=False),
            ),
            models.Index(fields=["es_version_vigente", "activo", "id_carpeta"]),
        ]
        # Permisos adicionales sobre documentos
        permissions = [
            (
                "puede_eliminar_cualquier_documento",
                "Puede eliminar documentos de cualquier usuario",
            ),
            (
                "puede_editar_cualquier_documento",
                "Puede editar documentos de cualquier usuario",
            ),
            (
                "puede_ver_documentos_restringidos",
                "Puede ver documentos que normalmente no le corresponden",
            ),
        ]

    def __str__(self):
        return f"{self.nombre_original} v{self.version} ({self.get_estado_display()})"

    def liberar_bloqueo(self):
        """Libera el bloqueo si ha expirado (por ejemplo, después de 30 minutos)."""
        if self.fecha_bloqueo and (timezone.now() - self.fecha_bloqueo).seconds > 1800:
            self.bloqueado_por = None
            self.fecha_bloqueo = None
            self.save(update_fields=["bloqueado_por", "fecha_bloqueo"])

    def finalizar_edicion(self):
        """
        Lógica para convertir un borrador en una versión oficial
        y quitarle la vigencia a la versión anterior.
        """
        if self.id_documento_padre:
            # Quitamos la vigencia a la versión anterior (el padre)
            self.id_documento_padre.es_version_vigente = False
            self.id_documento_padre.save()

        self.estado = "PENDIENTE"
        self.es_version_vigente = True
        self.save()


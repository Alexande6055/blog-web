import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils import timezone


# ============================
# 1. DEPARTAMENTO Y SUCURSAL
# ============================
class Departamento(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(
        default=True
    )  # Campo para habilitar/deshabilitar departamento sin eliminarlo de la DB

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Departamento"
        verbose_name_plural = "Departamentos"


class Sucursal(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    direccion = models.CharField(max_length=255)
    ruta_base_nas = models.CharField(
        max_length=500, help_text="Ruta raíz en el NAS para esta sucursal"
    )
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(
        default=True
    )  # Campo para habilitar/deshabilitar sucursal sin eliminarla de la DB

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.nombre


# ============================
# 2. USUARIO (extiende AbstractUser)
# ============================
class User(AbstractUser):
    # Campos adicionales
    nombre_completo = models.CharField(max_length=255)
    ci = models.CharField(
        max_length=20, unique=True, verbose_name="Cédula de Identidad", db_index=True
    )
    cargo = models.CharField(max_length=100, blank=True)

    # Relaciones con sucursal y departamento (SET_NULL porque si se eliminan, no queremos perder el usuario)
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios",
    )

    # Auditoría (update_at)
    update_at = models.DateTimeField(auto_now=True)

    # Note: date_joined ya existe en AbstractUser (fecha de creación)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        # Permisos personalizados (se crearán con makemigrations)
        permissions = [
            ("puede_aprobar_documentos", "Puede aprobar documentos pendientes"),
            ("puede_ver_logs", "Puede ver los logs del sistema"),
            ("puede_gestionar_usuarios", "Puede crear y editar usuarios"),
            ("puede_gestionar_tipos_documento", "Puede gestionar tipos de documento"),
            ("puede_ver_historial", "Puede ver historial de cambios de documentos"),
            ("puede_ver_visualizaciones", "Puede ver quién visualizó documentos"),
        ]

    def __str__(self):
        return f"{self.nombre_completo} ({self.username})"


# ============================
# 2. CARPETA
# ============================
class Carpeta(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    nombre_nas = models.SlugField(
        max_length=150, help_text="Nombre físico en el NAS (sin espacios ni tildes)"
    )
    # IMPORTANTE: Cambiado es PROTECT para evitar borrado físico accidental de la DB
    padre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcarpetas",
    )

    # Organización
    sucursal = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT, related_name="carpetas"
    )
    departamento = models.ForeignKey(
        Departamento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="carpetas",
    )

    # Campo para borrado lógico (Ocultar en el sistema)
    activo = models.BooleanField(default=True, db_index=True)

    # Auditoría básica
    creado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="carpetas_creadas"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    @property
    def ruta_fisica_completa(self):
        """Calcula la ruta absoluta en el NAS de forma recursiva."""
        if self.padre:
            return os.path.join(self.padre.ruta_fisica_completa, self.nombre_nas)
        return os.path.join(self.sucursal.ruta_base_nas, self.nombre_nas)

    def esta_visible(self):
        """Verifica si esta carpeta y todos sus ancestros están activos."""
        if not self.activo or not self.sucursal.activo:
            return False
        if self.padre:
            return self.padre.esta_visible()
        return True

    def obtener_sucursal(self):
        """Busca la sucursal hacia arriba en el árbol si no está definida."""
        if self.sucursal:
            return self.sucursal
        return self.padre.obtener_sucursal() if self.padre else None

    class Meta:
        verbose_name = "Carpeta"
        verbose_name_plural = "Carpetas"
        unique_together = ("nombre_nas", "padre", "sucursal")
        indexes = [
            models.Index(fields=["activo"]),
        ]

    def __str__(self):
        estado = "" if self.activo else "[OCULTA] "
        return f"{estado}{self.nombre} ({self.sucursal.nombre})"


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
        User,
        on_delete=models.PROTECT,  # No se puede eliminar usuario que subió documentos
        related_name="documentos_subidos",
    )
    id_sucursal = models.ForeignKey(
        Sucursal, on_delete=models.PROTECT, related_name="documentos"
    )
    id_tipo_documento = models.ForeignKey(
        TipoDocumento, on_delete=models.PROTECT, related_name="documentos"
    )
    id_carpeta = models.ForeignKey(
        Carpeta,
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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documentos_bloqueados",
    )
    fecha_bloqueo = models.DateTimeField(null=True, blank=True)

    # Aprobación
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    id_usuario_aprobacion = models.ForeignKey(
        User,
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


# ============================
# 5. NOTIFICACIONES ENVIADAS
# ============================
class Notificacion(models.Model):
    TIPO_CHOICES = [
        ("APROBACION", "Documento aprobado"),
        ("RECHAZO", "Documento rechazado"),
        ("SOLICITUD_CAMBIO", "Solicitud de cambios"),
        ("ACCESO_LOG", "Acceso temporal a logs"),
        ("NUEVO_DOC", "Nuevo documento pendiente"),
    ]

    usuario_destino = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notificaciones"
    )
    documento = models.ForeignKey(
        Archivo,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notificaciones",
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    asunto = models.CharField(max_length=255)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        indexes = [
            models.Index(fields=["usuario_destino", "leida"]),
            models.Index(fields=["fecha_envio"]),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.usuario_destino.username} - {self.fecha_envio}"


# ============================
# 6. REGISTRO DE ACCESOS A DOCUMENTOS (VISUALIZACIONES / DESCARGAS)
# ============================
class AccesoDocumento(models.Model):
    TIPO_CHOICES = [
        ("VISUALIZACION", "Visualización"),
        ("DESCARGA", "Descarga"),
        ("INTENTO_FALLIDO", "Intento fallido"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accesos")
    documento = models.ForeignKey(
        Archivo, on_delete=models.CASCADE, related_name="accesos"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_acceso = models.DateTimeField(auto_now_add=True, db_index=True)
    direccion_ip = models.GenericIPAddressField()
    exito = models.BooleanField(default=True)  # Para intentos fallidos

    class Meta:
        verbose_name = "Acceso a documento"
        verbose_name_plural = "Accesos a documentos"
        indexes = [
            models.Index(fields=["documento", "tipo"]),
            models.Index(fields=["usuario", "fecha_acceso"]),
        ]

    def __str__(self):
        return (
            f"{self.usuario.username} - {self.tipo} - {self.documento.nombre_original}"
        )


# ============================
# 7. LOGS DEL SISTEMA
# ============================
class EventoLog(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    tipo = models.CharField(max_length=50)  # Ej: 'UPDATE', 'DELETE', 'LOGIN', 'ACCESO'
    modulo = models.CharField(max_length=50)  # Ej: 'USUARIOS', 'DOCUMENTOS', 'AUTH'

    class Meta:
        verbose_name = "Evento de Log"
        verbose_name_plural = "Eventos de Log"

    def __str__(self):
        return f"{self.modulo} - {self.nombre}"


class Log(models.Model):
    RESULTADO_CHOICES = [
        ("EXITO", "Éxito"),
        ("ERROR", "Error"),
    ]

    evento = models.ForeignKey(EventoLog, on_delete=models.CASCADE, related_name="logs")
    usuario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="logs"
    )
    direccion_ip = models.GenericIPAddressField()
    fecha_hora = models.DateTimeField(auto_now_add=True, db_index=True)
    resultado = models.CharField(max_length=10, choices=RESULTADO_CHOICES)
    detalle = models.TextField()

    # Campos denormalizados para auditoría (por si el usuario se elimina)
    email = models.EmailField(null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    ci = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        indexes = [
            models.Index(fields=["fecha_hora"]),
            models.Index(fields=["usuario", "fecha_hora"]),
            models.Index(fields=["evento", "resultado"]),
        ]

    def __str__(self):
        return f"{self.fecha_hora} - {self.username or self.usuario} - {self.evento.nombre}"

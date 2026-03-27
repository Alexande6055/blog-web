import os
from django.db import models
from django.conf import settings


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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notificaciones",
    )
    documento = models.ForeignKey(
        "archivo.Archivo",
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

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accesos"
    )
    documento = models.ForeignKey(
        "archivo.Archivo", on_delete=models.CASCADE, related_name="accesos"
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
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
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

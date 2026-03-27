from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Campos adicionales
    nombre_completo = models.CharField(max_length=255)
    ci = models.CharField(
        max_length=20, unique=True, verbose_name="Cédula de Identidad", db_index=True
    )
    cargo = models.CharField(max_length=100, blank=True)

    # Relaciones con sucursal y departamento (SET_NULL porque si se eliminan, no queremos perder el usuario)
    departamento_sucursal = models.ForeignKey(
        "departamento_sucursal.DepartamentoSucursal",
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

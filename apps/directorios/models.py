from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group
from pathlib import Path


class Carpeta(models.Model):
    nombre = models.CharField(max_length=150)
    nombre_nas = models.SlugField(
        max_length=150, help_text="Nombre físico en el NAS (sin espacios ni tildes)"
    )
    # IMPORTANTE: PROTECT evita borrado físico accidental
    padre = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="subcarpetas",
    )


    departamento_sucursal = models.ForeignKey(
        "departamento_sucursal.DepartamentoSucursal",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="carpetas",
    )

    # Borrado lógico
    activo = models.BooleanField(default=True, db_index=True)

    # Auditoría
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="carpetas_creadas",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # ------------------------------------------------------------
    # Métodos principales
    # ------------------------------------------------------------
    @property
    def ruta_fisica_completa(self):
        """Calcula la ruta absoluta en el NAS usando pathlib (compatible con distintos SO)."""
        if self.padre:
            return str(Path(self.padre.ruta_fisica_completa) / self.nombre_nas)
        # Para carpetas raíz, usamos la ruta base del NAS
        return str(Path(settings.NAS_ROOT_PATH) / self.nombre_nas)

    @property
    def esta_visible(self):
        """Verifica si la carpeta y sus ancestros están activos, respetando la sucursal en la raíz."""
        if not self.activo:
            return False
        if self.padre:
            return self.padre.esta_visible()
        # Al llegar a la raíz, se verifica la sucursal (si existe)
        sucursal = self.obtener_sucursal()
        # Si no tiene sucursal o la sucursal está activa, es visible
        return sucursal is None or sucursal.activo

    def obtener_sucursal(self):
        """Busca la sucursal asociada (puede heredarse del padre si no está definida)."""
        if self.departamento_sucursal:
            return self.departamento_sucursal.sucursal
        return self.padre.obtener_sucursal() if self.padre else None

    def save(self, *args, **kwargs):
        """Validaciones adicionales antes de guardar."""
        # Evitar que una carpeta sea su propio padre (ciclo directo)
        if self.padre and self.padre.pk == self.pk:
            raise ValidationError("Una carpeta no puede ser padre de sí misma.")

        # Detectar ciclos más profundos recorriendo ancestros
        if self.padre:
            nodo = self.padre
            while nodo.padre:
                if nodo.padre == self:
                    raise ValidationError(
                        "No se puede crear un ciclo en la jerarquía de carpetas."
                    )
                nodo = nodo.padre

        super().save(*args, **kwargs)

    def tiene_permiso(self, usuario, nivel_requerido):
        """Devuelve True si el usuario tiene al menos el nivel_requerido en esta carpeta."""
        jerarquia = {"LECTURA": 1, "ESCRITURA": 2, "ADMIN": 3}
        nivel_usuario = PermisoCarpeta.nivel_permiso_usuario(usuario, self)
        if not nivel_usuario:
            return False
        return jerarquia.get(nivel_usuario, 0) >= jerarquia.get(nivel_requerido, 0)

    # ------------------------------------------------------------
    # Representación
    # ------------------------------------------------------------
    def __str__(self):
        estado = "" if self.activo else "[OCULTA] "
        sucursal = self.obtener_sucursal()
        ubicacion = sucursal.nombre if sucursal else "RAÍZ GLOBAL"
        return f"{estado}{self.nombre} ({ubicacion})"

    class Meta:
        verbose_name = "Carpeta"
        verbose_name_plural = "Carpetas"
        constraints = [
            models.UniqueConstraint(
                fields=["nombre_nas", "padre", "departamento_sucursal"],
                name="unique_nombre_nas_padre_departamento_sucursal",
            ),
        ]
        indexes = [
            models.Index(fields=["activo"]),
        ]


# ============================
#  2. PERMISOS DE USUARIOS POR CARPETA
# ============================
class PermisoCarpeta(models.Model):
    NIVEL_CHOICES = [
        ("LECTURA", "Solo Ver"),
        ("ESCRITURA", "Ver, Subir y Editar Archivos"),
        ("ADMIN", "Control Total"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="permisos_directos",
    )
    grupo = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="permisos_carpetas",
    )
    carpeta = models.ForeignKey(
        Carpeta, on_delete=models.CASCADE, related_name="permisos"
    )
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default="LECTURA")

    def clean(self):
        if not self.usuario and not self.grupo:
            raise ValidationError(
                "Debe especificar un usuario o un grupo para el permiso."
            )
        # Opcional: evitar que se asigne ambos a la vez si tu lógica lo requiere
        # if self.usuario and self.grupo:
        #     raise ValidationError("Un permiso no puede pertenecer a un usuario y a un grupo a la vez.")
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def nivel_permiso_usuario(cls, usuario, carpeta):
        """
        Retorna el nivel de permiso efectivo del usuario sobre la carpeta.
        Prioridad: permiso directo > permiso por grupo (el primero encontrado).
        """
        # Permiso directo
        permiso_directo = cls.objects.filter(carpeta=carpeta, usuario=usuario).first()
        if permiso_directo:
            return permiso_directo.nivel

        # Permiso a través de grupos
        grupos_usuario = usuario.groups.all()
        permiso_grupo = cls.objects.filter(
            carpeta=carpeta, grupo__in=grupos_usuario
        ).first()
        if permiso_grupo:
            return permiso_grupo.nivel

        return None

    class Meta:
        verbose_name = "Permiso de Carpeta"
        verbose_name_plural = "Permisos de Carpetas"
        constraints = [
            models.UniqueConstraint(
                fields=["carpeta", "usuario"],
                condition=models.Q(usuario__isnull=False),
                name="unique_permiso_usuario",
            ),
            models.UniqueConstraint(
                fields=["carpeta", "grupo"],
                condition=models.Q(grupo__isnull=False),
                name="unique_permiso_grupo",
            ),
        ]
        indexes = [
            models.Index(fields=["carpeta", "usuario"]),
            models.Index(fields=["carpeta", "grupo"]),
        ]

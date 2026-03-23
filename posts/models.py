from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. Entidad Departamento
class Departamento(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# 2. Entidad Sucursal
class Sucursal(models.Model):
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.nombre

# 3. Entidad Usuario (Extendiendo AbstractUser)
class User(AbstractUser):
    # Campos heredados de AbstractUser que YA NO necesitas declarar:
    # id, password, username, email, is_staff, is_active, date_joined, 
    # groups (Tus Roles), user_permissions (Tus Permisos específicos)

    nombre_completo = models.CharField(max_length=255)
    ci = models.CharField(max_length=20, unique=True, verbose_name="Cédula de Identidad")
    cargo = models.CharField(max_length=100)
    
    # Relaciones ManyToOne
    departamento = models.ForeignKey(
        Departamento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="usuarios"
    )
    sucursal = models.ForeignKey(
        Sucursal, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="usuarios"
    )

    # Auditoría (date_joined ya es el CreateDateColumn)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre_completo} ({self.username})"


##Entidades para los logs del sistema
class EventoLog(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50) # Ejemplo: 'UPDATE', 'DELETE', 'LOGIN'
    modulo = models.CharField(max_length=50) # Ejemplo: 'USUARIOS', 'SUCURSALES'

    def __str__(self):
        return f"{self.modulo} - {self.nombre}"

class Log(models.Model):
    RESULTADO_CHOICES = [
        ('EXITO', 'Éxito'),
        ('ERROR', 'Error'),
    ]

    evento = models.ForeignKey(EventoLog, on_delete=models.CASCADE)
    id_auth = models.IntegerField(null=True, blank=True)
    direccion_ip = models.GenericIPAddressField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    resultado = models.CharField(max_length=10, choices=RESULTADO_CHOICES)
    detalle = models.TextField()
    
    # Campos informativos (denormalizados para auditoría rápida)
    email = models.EmailField(null=True, blank=True)
    user = models.CharField(max_length=150, null=True, blank=True)
    ci = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.fecha_hora} - {self.user} - {self.evento.nombre}"

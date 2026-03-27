from django.db import models


#Modelo departamento
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

#Modelo sucursal
class Sucursal(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(
        default=True
    )  # Campo para habilitar/deshabilitar sucursal sin eliminarla de la DB

    class Meta:
        verbose_name = "Sucursal"
        verbose_name_plural = "Sucursales"

    def __str__(self):
        return self.nombre

#Tabla intermedia para relacionar departamentos y sucursales (muchos a muchos)
class DepartamentoSucursal(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.PROTECT)

    class Meta:
        unique_together = ("departamento", "sucursal")  # Evita duplicados
        verbose_name = "Departamento-Sucursal"
        verbose_name_plural = "Departamentos-Sucursales"

    def __str__(self):
        return f"{self.departamento.nombre} - {self.sucursal.nombre}"

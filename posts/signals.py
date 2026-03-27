import os
from pathlib import Path
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.directorios.models import Carpeta
from config.settings import NAS_ROOT_PATH
@receiver(post_save, sender=Carpeta)
def crear_directorio_nas(sender, instance, created, **kwargs):
    print(f"DEBUG: Señal disparada para {instance.nombre}. Creado: {created}")
    print(f"DEBUG: Señal disparada para {instance.nombre_original}. Creado: {created}")
    """
    Crea la estructura física de carpetas en el NAS de forma jerárquica.
    Si la carpeta no tiene padre, se crea en la raíz del Simulador-nas.
    Si tiene padre, construye la ruta desde la raíz hasta la subcarpeta.
    """
    if created:
        # 1. Definimos la raíz absoluta en el servidor

        # 2. Construimos la jerarquía de carpetas recorriendo hacia arriba
        partes_ruta = []
        curr = instance

        while curr is not None:
            # Usamos 'nombre_nas' porque es el SlugField diseñado para el sistema de archivos
            # Si prefieres usar 'nombre', mantén: curr.nombre.replace(" ", "_")
            partes_ruta.insert(0, curr.nombre_nas)  # Insertamos al inicio para mantener el orden correcto

            # Subimos al padre. El bucle terminará cuando curr.padre sea None (Carpeta Raíz)
            curr = curr.padre

        # 3. Unimos la base con todas las partes de la jerarquía
        # Ejemplo: C:\...\Simulador-nas / 2026 / Sucursal_Quito / Contabilidad
        ruta_final = NAS_ROOT_PATH.joinpath(*partes_ruta)

        try:
            # parents=True: Crea '2026' y 'Sucursal_Quito' si aún no existen físicamente.
            # exist_ok=True: No lanza error si la carpeta ya fue creada previamente.
            ruta_final.mkdir(parents=True, exist_ok=True)
            print(f"✅ Directorio creado exitosamente en NAS: {ruta_final}")
        except Exception as e:
            # Es vital capturar errores de permisos o rutas inexistentes
            print(f"❌ Error crítico al crear directorio en NAS: {e}")

from apps.departamento_sucursal.modelos import Sucursal


def obtener_sucursales_listar():
    """
    Retorna una lista de diccionarios con id y nombre de las sucursales activas.
    """
    return list(
        Sucursal.objects.filter(activo=True)
        .order_by("id")
        .values("id", "nombre")
    )

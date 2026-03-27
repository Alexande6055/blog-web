from apps.departamento_sucursal.modelos import Departamento

def obtener_departamentos_listar():
    """
    Retorna una lista de diccionarios con id y nombre de los departamentos activos.
    """
    return list(
        Departamento.objects.filter(activo=True)
        .order_by("id")
        .values("id", "nombre")
    )

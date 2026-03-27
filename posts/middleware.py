from .models import Log, EventoLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesar la petición primero
        response = self.get_response(request)

        # Solo loguear si el usuario está autenticado y son métodos que cambian datos
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Mapeo de acciones a eventos predefinidos
            # Ajusta según tus URLs y necesidades
            evento_nombre = self.obtener_evento(request)
            if evento_nombre:
                try:
                    evento = EventoLog.objects.get(nombre=evento_nombre)
                except EventoLog.DoesNotExist:
                    # Si el evento no existe, lo registramos como error en logs pero no creamos
                    # Podrías crear el evento aquí con manejo de excepciones, pero es mejor precargarlo
                    return response

                # Extraer IP
                ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]

                # Crear el Log
                Log.objects.create(
                    evento=evento,
                    usuario=request.user,
                    direccion_ip=ip,
                    resultado='EXITO' if response.status_code < 400 else 'ERROR',
                    detalle=f"URL: {request.path} - Data: {request.POST.dict()}",
                    email=request.user.email,
                    username=request.user.username,
                    ci=getattr(request.user, 'ci', '')
                )

        return response

    def obtener_evento(self, request):
        """
        Devuelve el nombre del evento predefinido según la URL y método.
        """
        path = request.path
        method = request.method

        # Ejemplo: login
        if path == '/login/' and method == 'POST':
            return 'LOGIN_EXITOSO' if request.user.is_authenticated else 'LOGIN_FALLIDO'
        # Subida de documento
        if path == '/documentos/subir/' and method == 'POST':
            return 'CREAR_DOCUMENTO'
        # Aprobación
        if path.startswith('/documentos/aprobar/') and method == 'POST':
            return 'APROBAR_DOCUMENTO'
        # etc.

        # Si no se mapea, podrías usar un evento genérico
        return f'ACCION_{method}_{path.split("/")[1].upper()}'
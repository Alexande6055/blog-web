import json
from .models import Log, EventoLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Procesar la petición primero
        response = self.get_response(request)

        # 2. Solo logueamos si el usuario está autenticado y son métodos que cambian datos
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            
            # Intentamos determinar el evento basado en la URL o el método
            # Esto es un ejemplo, podrías hacerlo más dinámico
            evento, _ = EventoLog.objects.get_or_create(
                nombre=f"Acción {request.method}",
                modulo=request.path.split('/')[1].upper(),
                tipo=request.method
            )

            # Extraer IP
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]

            # Crear el Log
            Log.objects.create(
                evento=evento,
                id_auth=request.user.id,
                direccion_ip=ip,
                resultado='EXITO' if response.status_code < 400 else 'ERROR',
                detalle=f"URL: {request.path} - Data: {request.POST.dict()}",
                email=request.user.email,
                user=request.user.username,
                ci=getattr(request.user, 'ci', '') # Usamos getattr por seguridad
            )

        return response
import json
from .models import Log, EventoLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Procesar la petición primero para obtener la respuesta y el status_code
        response = self.get_response(request)

        # 2. Filtrar: Solo usuarios autenticados y métodos de escritura
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            
            # Obtener o crear el evento (Asegúrate de que coincida con tus campos de EventoLog)
            modulo_name = request.path.split('/')[1].upper() if len(request.path.split('/')) > 1 else 'RAIZ'
            
            evento, _ = EventoLog.objects.get_or_create(
                nombre=f"{request.method} en {request.path}",
                defaults={
                    'modulo': modulo_name,
                    'tipo': request.method
                }
            )

            # Extraer IP de forma segura
            x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')

            # 3. Crear el Log con los nombres de campos CORRECTOS
            Log.objects.create(
                evento=evento,
                usuario=request.user,          # Campo ForeignKey en tu modelo
                direccion_ip=ip,
                resultado='EXITO' if response.status_code < 400 else 'ERROR',
                detalle=f"Path: {request.path} | Status: {response.status_code} | POST_DATA: {request.POST.dict()}",
                
                # Campos denormalizados (Copia de seguridad)
                email=request.user.email,
                username=request.user.username, # En tu modelo se llama 'username', no 'user'
                ci=getattr(request.user, 'ci', '') 
            )

        return response
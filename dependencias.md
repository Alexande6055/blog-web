# Activar entorno virtual 
.\env\Scripts\activate


pip install django
pip install django-import-export
pip install psycopg2-binary

# Ejecutamos el servidor 
python manage.py runserver

# Creaciuon superUsuario
python manage.py createsuperuser
# Crear migraciones 
python manage.py makemigrations
## Forzamos
python manage.py makemigrations posts --name initial
## ejecutamos
python manage.py migrate


# Estructuracion
1. Organización del Backend en la App
Dentro de tu carpeta posts, ya tienes los archivos esenciales (models.py, views.py). Sin embargo, a medida que el proyecto crece, el backend se beneficia de separar las responsabilidades:

models.py (La Base de Datos): Aquí defines tus tablas. Usa nombres de clase en singular (ej: Post en lugar de Posts).

urls.py (Rutas de la App): Te falta un urls.py dentro de la carpeta posts. Es mejor tener las rutas de la app ahí y luego incluirlas en config/urls.py usando include().

admin.py: Registra tus modelos aquí para poder verlos en el panel de administración de Django (/admin).

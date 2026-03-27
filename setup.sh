#!/bin/bash
echo "Creando entorno virtual..."
python3 -m venv env

echo "Activando entorno virtual..."
source env/bin/activate

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Realizando migraciones..."
python manage.py migrate

echo "Creando superusuario (opcional)..."
python manage.py createsuperuser --noinput || echo "Si quieres crear superusuario manualmente, ejecuta: python manage.py createsuperuser"

echo "Proceso completado."
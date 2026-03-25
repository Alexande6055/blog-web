from django.contrib import admin
from django.urls import path
from posts import views  # Importamos el archivo completo para acceder a todas las funciones
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name="home"),
    # Ruta del Login: Esencial para que el redirect('login') funcione
    path('login/', views.login_view, name='login'),
    path('buscar-roles/', views.buscar_roles, name='buscar_roles'),
    # Ruta para obtener el formulario de un rol (para HTMX)
    path('rol/formulario/', views.get_rol_form, name='rol_formulario'),
    path('rol/formulario/<int:rol_id>/', views.get_rol_form, name='rol_formulario_edit'),
    path('editar/<int:edit_id>/', views.home, name="home_edit"), # Misma vista, diferente comportamiento
    # Ruta de Logout
    path('logout/', views.logout_view, name='logout'),
]

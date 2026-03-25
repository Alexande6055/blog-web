from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from posts.selectors.permisos import listar_permisos
from posts.selectors.roles import listar_roles, obtener_rol_con_permisos  # Importante
from posts.services.services_roles import update_rol, create_rol
import json

# --- RUTAS PROTEGIDAS (Equivalente a <ProtectedRoute>) ---
# @login_required
# def editar_rol(request, rol_id):
#    rol = get_object_or_404(Group, id=rol_id)

#    if request.method == 'POST':
# 1. Guardamos los cambios
#        rol.name = request.POST.get('nombre')
#        rol.save()

# 2. Redirigimos al NOMBRE de la URL que maneja el index
#        return redirect('home')

# Si entras por GET (para ver el formulario de edición)
#    return render(request, "posts/editar_rol.html", {"rol": rol})


@login_required
def buscar_roles(request):
    search = request.POST.get("search")
    # Lógica para buscar roles
    return render(request, "posts/buscar_roles.html", {"search": search})


@login_required
def home(request, edit_id=None):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        permisos_json = request.POST.get("permissions", "[]")
        try:
            permisos_ids = json.loads(permisos_json)  # lista de ids
        except json.JSONDecodeError:
            permisos_ids = []

        if edit_id:
            update_rol(
                edit_id, nombre, permisos_ids
            )  # asegúrate de que update_rol reciba lista de ids
        else:
            create_rol(nombre, permisos_ids)

        # SI ES HTMX: Devolvemos solo la tabla, no toda la página
        if request.headers.get('HX-Request'):
            roles = listar_roles() # Refrescamos la lista de la DB
            return render(request, "includes/snippets/_tabla_roles.html", {"roles": roles})

        # Si no es HTMX (fallback), redireccionamos normal
        return redirect("home")
    # --- Lógica del GET (Carga inicial) ---
    roles = listar_roles()
    # Datos para el formulario (si estamos editando)
    rol_a_editar = None
    permisos_disponibles = None
    if edit_id:
        data = obtener_rol_con_permisos(edit_id)
        rol_a_editar = data["rol"]
        permisos_disponibles = data["permisos_disponibles"]
    else:
        permisos_disponibles = listar_permisos()

    return render(
        request,
        "posts/index.html",
        {
            "roles": roles,
            "rol_a_editar": rol_a_editar,
            "permisos_disponibles": permisos_disponibles,
        },
    )


@login_required
def user_administrator(request):
    # Equivalente a tu ruta /user-administrator
    return render(request, "posts/user_admin.html")


# --- RUTAS PÚBLICAS (Equivalente a <PublicRoute>) ---


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")  # Si ya está logueado, no le dejes ver el login

    error = None
    if request.method == "POST":
        usuario = request.POST.get("username")
        clave = request.POST.get("password")
        user = authenticate(request, username=usuario, password=clave)

        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            error = "Usuario o contraseña incorrectos"

    return render(request, "posts/login.html", {"error": error})


def logout_view(request):
    auth_logout(request)
    return redirect("login")

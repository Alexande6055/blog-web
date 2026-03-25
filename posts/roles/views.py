import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.shortcuts import redirect, render
from django.views import View

from posts.selectors.permisos import listar_permisos
from posts.selectors.roles import listar_roles, obtener_rol_con_permisos
from posts.services.services_roles import create_rol, update_rol


class RolFormView(LoginRequiredMixin, View):
    """
    Devuelve el formulario del rol para HTMX.
    - Si hay `rol_id`: precarga para editar.
    - Si no hay `rol_id`: devuelve formulario vacío para crear.
    """

    def get(self, request, rol_id=None, *args, **kwargs):
        if rol_id:
            data = obtener_rol_con_permisos(rol_id)
            rol_a_editar = data["rol"]
            permisos_disponibles = data["permisos_disponibles"]
        else:
            rol_a_editar = None
            permisos_disponibles = listar_permisos()

        return render(
            request,
            "includes/formularios/create_edit_grupo_form.html",
            {
                "rol_a_editar": rol_a_editar,
                "permisos_disponibles": permisos_disponibles,
            },
        )


class RolesHomeView(LoginRequiredMixin, View):
    """
    Vista principal de gestión de Roles (Groups) + envío HTMX del listado.
    """

    def get(self, request, edit_id=None, *args, **kwargs):
        roles = listar_roles()

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
            "roles/index.html",
            {
                "roles": roles,
                "rol_a_editar": rol_a_editar,
                "permisos_disponibles": permisos_disponibles,
            },
        )

    def post(self, request, edit_id=None, *args, **kwargs):
        nombre = request.POST.get("nombre", "").strip()
        permisos_json = request.POST.get("permissions", "[]")

        if not nombre:
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "includes/snippets/_tabla_roles.html",
                    {"error": "El nombre del grupo es requerido", "roles": listar_roles()},
                )
            return redirect("home")

        try:
            permisos_ids = json.loads(permisos_json)  # lista de ids
        except json.JSONDecodeError:
            permisos_ids = []

        try:
            if edit_id:
                update_rol(edit_id, nombre, permisos_ids)
            else:
                create_rol(nombre, permisos_ids)
        except Exception as e:
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "includes/snippets/_tabla_roles.html",
                    {"error": f"Error: {str(e)}", "roles": listar_roles()},
                )
            return redirect("home")

        # Si es HTMX: devolvemos solo la tabla
        if request.headers.get("HX-Request"):
            roles = listar_roles()
            return render(request, "includes/snippets/_tabla_roles.html", {"roles": roles})

        return redirect("home")


class BuscarRolesView(LoginRequiredMixin, View):
    """
    Búsqueda de roles por nombre.
    - Soporta `GET ?search=...` (y también `POST search=...` por compatibilidad).
    - Devuelve snippet si es HTMX, o la página completa si no lo es.
    """

    def get(self, request, *args, **kwargs):
        search = request.GET.get("search", "").strip()
        return self._handle_search(request, search=search)

    def post(self, request, *args, **kwargs):
        search = request.POST.get("search", "").strip()
        return self._handle_search(request, search=search)

    def _handle_search(self, request, search: str):
        if not search:
            roles = listar_roles()
        else:
            # Incluir el conteo es útil si algún snippet lo necesita.
            roles = (
                Group.objects.annotate(total_permisos=Count("permissions"))
                .filter(name__icontains=search)
            )

        if request.headers.get("HX-Request"):
            return render(request, "includes/snippets/_tabla_roles.html", {"roles": roles})

        return render(
            request,
            "roles/index.html",
            {
                "roles": roles,
                "rol_a_editar": None,
                "permisos_disponibles": listar_permisos(),
            },
        )


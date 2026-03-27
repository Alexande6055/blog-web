import json
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from apps.Permisos.selectors.permisos import listar_permisos
from apps.Roles_grupos.services.services_roles import create_rol, update_rol
from apps.Roles_grupos.selectors.roles import listar_roles,obtener_rol_con_permisos


class RolesHomeView(LoginRequiredMixin, View):
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
            "pages/list_roles.html",
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
                    "snippets/_tabla_roles.html",
                    {
                        "error": "El nombre del grupo es requerido",
                        "roles": listar_roles(),
                    },
                )
            return redirect("home")

        try:
            permisos_ids = json.loads(permisos_json)
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
                    "snippets/_tabla_roles.html",
                    {"error": f"Error: {str(e)}", "roles": listar_roles()},
                )
            return redirect("home")

        if request.headers.get("HX-Request"):
            roles = listar_roles()
            return render(
                request, "ui/snippets/_tabla_roles.html", {"roles": roles}
            )

        return redirect("home")

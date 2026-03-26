from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import  render
from django.views import View
from apps.Roles_grupos.selectors.roles import obtener_rol_con_permisos
from apps.Permisos.selectors.permisos import listar_permisos

class RolFormView(LoginRequiredMixin, View):
    def get(self, request, rol_id=None, *args, **kwargs):
        if rol_id:
            data = obtener_rol_con_permisos(rol_id)
            rol_a_editar = data['rol']
            permisos_disponibles = data['permisos_disponibles']
        else:
            rol_a_editar = None
            permisos_disponibles = listar_permisos()

        return render(
            request,
            'includes/formularios/create_edit_grupo_form.html',
            {
                'rol_a_editar': rol_a_editar,
                'permisos_disponibles': permisos_disponibles,
            },
        )


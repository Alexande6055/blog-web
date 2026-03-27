from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Count
from django.shortcuts import  render
from django.views import View
from apps.Permisos.selectors.permisos import listar_permisos
from apps.Roles_grupos.selectors.roles import listar_roles

class BuscarRolesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        search = request.GET.get('search', '').strip()
        return self._handle_search(request, search=search)

    def post(self, request, *args, **kwargs):
        search = request.POST.get('search', '').strip()
        return self._handle_search(request, search=search)

    def _handle_search(self, request, search: str):
        if not search:
            roles = listar_roles()
        else:
            roles = (
                Group.objects.annotate(total_permisos=Count('permissions'))
                .filter(name__icontains=search)
            )

        if request.headers.get('HX-Request'):
            return render(request, 'includes/snippets/_tabla_roles.html', {'roles': roles})

        return render(
            request,
            'pages/list_roles.html',
            {
                'roles': roles,
                'rol_a_editar': None,
                'permisos_disponibles': listar_permisos(),
            },
        )

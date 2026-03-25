"""
Este archivo se mantiene para compatibilidad con rutas existentes (`config/urls.py`).
La lógica real se movió a CBV en:
- `posts/auth/views.py`
- `posts/roles/views.py`
"""

from posts.auth.views import LoginView, LogoutView
from posts.roles.views import BuscarRolesView, RolFormView, RolesHomeView

# Roles / Groups
home = RolesHomeView.as_view()
get_rol_form = RolFormView.as_view()
buscar_roles = BuscarRolesView.as_view()

# Auth
login_view = LoginView.as_view()
logout_view = LogoutView.as_view()


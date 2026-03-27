
from django.shortcuts import redirect
from django.views import View
from django.contrib.auth import logout 
class LogoutView(View):
    """Logout y redirección al login."""

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.shortcuts import redirect, render
from django.views import View


class LoginView(View):
    """
    Login clásico (username/password) usando el template: `auth/login.html`.
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "auth/login.html", {"error": None})

    def post(self, request, *args, **kwargs):
        usuario = request.POST.get("username")
        clave = request.POST.get("password")

        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            auth_login(request, user)
            return redirect("home")

        return render(
            request,
            "auth/login.html",
            {"error": "Usuario o contraseña incorrectos"},
        )


class LogoutView(View):
    """Logout y redirección al login."""

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect("login")

    def post(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect("login")



from django.contrib.auth import authenticate,login
from django.shortcuts import redirect,render
from django.views import View
class LoginView(View):
    """
    Login clásico (username/password) usando el template: `login_personalizado/login.html`.
    """

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return render(request, "login.html", {"error": None})

    def post(self, request, *args, **kwargs):
        usuario = request.POST.get("username")
        clave = request.POST.get("password")

        user = authenticate(request, username=usuario, password=clave)
        if user is not None:
            login(request, user)
            return redirect("home")

        return render(
            request,
            "login.html",
            {"error": "Usuario o contraseña incorrectos"},
        )

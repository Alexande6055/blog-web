from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required # Importante

# --- RUTAS PROTEGIDAS (Equivalente a <ProtectedRoute>) ---

@login_required
def home(request):
    # Esta vista usará el Layout con Sidebar y Header
    return render(request, 'posts/index.html')

@login_required
def user_administrator(request):
    # Equivalente a tu ruta /user-administrator
    return render(request, 'posts/user_admin.html')


# --- RUTAS PÚBLICAS (Equivalente a <PublicRoute>) ---

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home') # Si ya está logueado, no le dejes ver el login
        
    error = None
    if request.method == 'POST':
        usuario = request.POST.get('username')
        clave = request.POST.get('password')
        user = authenticate(request, username=usuario, password=clave)
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            error = "Usuario o contraseña incorrectos"
            
    return render(request, 'posts/login.html', {'error': error})

def logout_view(request):
    auth_logout(request)
    return redirect('login')
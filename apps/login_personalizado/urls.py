from django.contrib import admin
from django.urls import path
from .views import logout_view,login_view
urlpatterns = [
    path("login/", login_view.LoginView.as_view(), name="login"),
    path("logout/", logout_view.LogoutView.as_view(), name="logout"),
]

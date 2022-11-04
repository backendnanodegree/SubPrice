from django.urls import path

from users.views import index, LoginView, SignUpView, logout_view

urlpatterns = [
    path("", index, name="index"),
    path("signup/", SignUpView.as_view(), name="sign_up"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
]
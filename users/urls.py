from django.urls import path

from users.views import index, LoginView, SignUpView, logout_view, myinfo, withdrawal, remove_picture

urlpatterns = [
    path("", index, name="index"),
    path("signup/", SignUpView.as_view(), name="sign_up"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("myinfo/", myinfo, name="myinfo"),
    path("withdrawal", withdrawal, name="withdrawal"),
    path("remove_picture", remove_picture, name="remove_picture"),
]
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView

from django.contrib.auth import login, logout, authenticate
from django.views.generic import FormView

from users.forms import LoginForm
# Create your views here.


class SignUpView(TemplateView):
    template_name = "users/sign_up.html"

class LoginView(FormView):
    """
    최선우 : form_valid 함수를 통해 로그인 요청 데이터의 인증 처리
    """
    template_name = "users/login.html"
    form_class = LoginForm
    success_url = "/subscriptions/main/"
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        email = form.data.get("email")
        password = form.data.get("password")
        user = authenticate(self.request, email=email, password=password)
        login(self.request, user)
        return super().form_valid(form)
    
    def form_invalid(self, form):
        return super().form_invalid(form)

def logout_view(request):
    pass

def index(request):
    return redirect("login")
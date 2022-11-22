from django.shortcuts import render, redirect

from django.contrib.auth import login, logout, authenticate
from django.views.generic import FormView

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash

from users.forms import LoginForm, SignUpForm, MyInfoForm
from users.models import User
# Create your views here.


def my_decorator(function):
    def decorator_func(request):
        if not request.user.is_anonymous:
            return redirect("main")
        return function(request)

    return decorator_func

@method_decorator(my_decorator, name="get")
class SignUpView(FormView):
    template_name = "users/sign_up.html"
    form_class = SignUpForm
    success_url = "/subscriptions/main/"
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        
        email = form.data.get("email")
        fullname = form.data.get("fullname")
        password = form.data.get("password")

        user = User.objects.create_user(email, fullname, password)

        user = authenticate(self.request, email=email, password=password)
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
    
@method_decorator(my_decorator, name="get")
class LoginView(FormView):
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

@login_required(login_url="login")
def myinfo(request):
    if request.method == 'POST':
        form = MyInfoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            old_data = User.objects.get(email=request.user)
            old_password = old_data.password
            user = form.save(commit=False)
            new_password = form.data.get("password")
            if new_password:
                user.set_password(new_password)
            else:
                user.password = old_password
            user.save()
            update_session_auth_hash(request, user)
            form = MyInfoForm(instance=request.user)
            context = {}
            context['form'] = form
            context['show_header'] = True
            context['success_msg'] = '정보가 수정되었습니다.'
            return render(request, 'users/myinfo.html', context)
    else:
        form = MyInfoForm(instance=request.user)
    context= {'form': form, 'show_header': True}
    return render(request, 'users/myinfo.html', context)

@login_required(login_url="login")
def remove_picture(request):
    if request.method == 'GET':
        user = User.objects.get(id=request.user.id)
        user.picture = None
        user.save()
        return redirect('myinfo') 

@login_required(login_url="login")
def withdrawal(request):
    if request.method == 'GET':
        user = User.objects.get(id=request.user.id)
        user.is_active = 0
        user.save()
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect("index")

def index(request):
    return redirect("login")
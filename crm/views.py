from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django import views
from crm.forms import RegisterForm
from crm.models import UserProfile


# Create your views here.
class LoginView(views.View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 获取用户输入的内容
        email = request.POST.get('email')
        password = request.POST.get('password')
        is_check = (request.POST.get('is_check', None) == '777')
        # 校验邮箱密码是否正确
        user_obj = auth.authenticate(request, email=email, password=password)
        if user_obj:
            # 登录成功
            # 存session数据并写回Cookie
            auth.login(request, user_obj)
            if is_check:
                request.session.set_expiry(7 * 24 * 60 * 60)
            else:
                request.session.set_expiry(0)
            return redirect('/index/')
        else:
            return render(request, 'login.html', {"error_msg": "邮箱或密码错误"})


class RegisterView(views.View):
    def get(self, request):
        form_obj = RegisterForm()
        return render(request, 'register.html', {'form_obj': form_obj})

    def post(self, request):
        form_obj = RegisterForm(request.POST)
        if form_obj.is_valid():
            # 校验通过
            # 1.先把 re_password 字段去掉
            form_obj.cleaned_data.pop('re_password')
            # 2.去数据库创建用户
            UserProfile.objects.create_user(**form_obj.cleaned_data)
            return redirect('/login/')
        else:
            return render(request, 'register.html', {'form_obj': form_obj})

@login_required
def index(request):
    return HttpResponse('index')

from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django import views


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


@login_required
def index(request):
    return HttpResponse('index')

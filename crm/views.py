from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.urls import reverse
from django import views
from django.db.models.query import Q
from django.http import QueryDict
from copy import deepcopy
from crm.forms import RegisterForm, CustomerForm, ConsultRecordForm, EnrollmentForm
from crm.models import UserProfile, Customer, ConsultRecord, Enrollment
from utils.myPagination import Pagination


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
    return redirect(reverse('customer_list'))


class CustomerListView(views.View):
    @method_decorator(login_required)
    def get(self, request):
        url_prefix = request.path_info
        # qd = deepcopy(request.GET)
        # qd._mutable = True
        qd = request.GET.copy()
        current_page = request.GET.get('page', 1)

        if request.path_info == reverse('my_customer'):
            # 获取私户信息（也就是当前登录用户的客户）
            query_set = Customer.objects.filter(consultant=request.user)
        else:
            # 获取所有公户信息
            query_set = Customer.objects.filter(consultant__isnull=True)

        # -------------------------------------------模糊检索---------------------------------------------
        # 根据模糊检索的条件对 query_set 再做过滤
        query = request.GET.get('query', '')
        # 找到 name、qq、qq_name 字段包含 query 的那些数据
        query_set = query_set.filter(Q(name__icontains=query) | Q(qq__icontains=query) | Q(qq_name__icontains=query))
        # ----------------------另一个方法：自己封装-------------------------
        # q = self._get_query_q(['name', 'qq', 'qq_name'])
        # data = query_set.filter(q)
        # ----------------------另一个方法：自己封装 END--------------------
        total_count = query_set.count()
        page_obj = Pagination(url_prefix, current_page, total_count, qd)
        data = query_set[page_obj.start: page_obj.end]

        # 获取当前 URL 作为操作后需要跳转回的 URL
        current_url = request.get_full_path()
        # 生成一个空的 QueryDict 对象
        query_params = QueryDict(mutable=True)
        # 添加一个 next 键值对
        query_params['next'] = current_url
        # 利用 QueryDict 内置的方法编码成 URL
        next_url = query_params.urlencode()

        return render(request, 'customer_list.html',
                      {'customer_list': data, 'next_url': next_url, 'page_obj': page_obj})

    @method_decorator(login_required)
    def post(self, request):
        """批量操作：变为公户/变为私户"""
        action = request.POST.get('action')
        cid = request.POST.getlist('cid')

        # if action == 'to_private':
        #     # 找到所有要操作的客户数据，把他们变成我的客户
        #     Customer.objects.filter(id__in=cid).update(consultant=request.user)
        # elif action == 'to_public':
        #     # 把我的客户数据变为公户数据
        #     Customer.objects.filter(id__in=cid).update(consultant=None)
        #
        # return redirect(reverse('customer_list'))

        # ---------------------------------利用 action 反射操作--------------------------------------------

        if not hasattr(self, action):
            return HttpResponse('滚')
        ret = getattr(self, action)(cid)
        if ret:
            return ret
        return redirect(reverse('customer_list'))

    def to_private(self, cid):
        update_num = len(cid)
        # 考虑到多个销售争抢同一个客户的情况
        from django.db import transaction
        with transaction.atomic():
            # 找到所有要操作的客户数据，把他们变成我的客户
            select_objs = Customer.objects.filter(id__in=cid, consultant__isnull=True).select_for_update()
            select_num = select_objs.count()
            # 如果查询出来的数据数目不等于想要更新的数量，说明有些被别人抢走了
            if select_num != update_num:
                # 拿到我可以转为私户的那些客户的id值
                select_ids = [i[0] for i in select_objs.values_list('id')]
                select_objs.update(consultant=self.request.user)
                # 谁被别人抢走了
                others = Customer.objects.filter(id__in=cid).exclude(id__in=select_ids)
                name_tuple = others.values_list('name')
                name_str = '、'.join([i[0] for i in name_tuple])
                return HttpResponse('手太慢了，{}已经被别人抢走了'.format(name_str))
            else:
                select_objs.update(consultant=self.request.user)

    def to_public(self, cid):
        Customer.objects.filter(id__in=cid).update(consultant=self.request.user)

    # ---------------------------------利用 action 反射操作 END--------------------------------------------

    # def _get_query_q(self, field_list, op='OR'):
    #     """定义一个模糊检索的私有方法"""
    #     # 从 URL 中取到 query 参数
    #     query = self.request.GET.get('query', '')
    #     q = Q()
    #     # 指定 q 查询内部的操作是 OR 还是 AND
    #     q.connector = op
    #     # 遍历要检索的字段，挨个添加子 Q 对象
    #     for field in field_list:
    #         q.children.append(Q(('{}__icontains'.format(field), query)))
    #     return q


def logout(request):
    auth.logout(request)
    return redirect('/login/')


"""
def add_customer(request):
    if request.method == 'POST':
        form_obj = CustomerForm(request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer_list'))
        else:
            return render(request, 'add_customer.html', {'form_obj': form_obj})

    form_obj = CustomerForm()
    return render(request, 'add_customer.html', {'form_obj': form_obj})


def edit_customer(request, edit_id):
    customer_obj = Customer.objects.filter(pk=edit_id).first()
    # 使用 instance 对象的数据填充生成 input 标签
    form_obj = CustomerForm(instance=customer_obj)
    if request.method == 'POST':
        # 使用 POST 提交的数据去更新指定的 instance 实例
        form_obj = CustomerForm(request.POST, instance=customer_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('customer_list'))

    return render(request, 'add_customer.html', {'form_obj': form_obj})
"""


# 新增和编辑二合一的视图函数
def customer(request, edit_id=None):
    # 如果 edit_id=None 表示是新增操作，如果 edit_id 有值表示是编辑操作
    customer_obj = Customer.objects.filter(pk=edit_id).first()  # 有值返回具体对象，否则返回 None
    # 使用 instance 对象的数据填充生成 input 标签
    form_obj = CustomerForm(instance=customer_obj)
    if request.method == 'POST':
        # 使用 POST 提交的数据去更新指定的 instance 实例
        form_obj = CustomerForm(request.POST, instance=customer_obj)
        if form_obj.is_valid():
            form_obj.save()
            next_url = request.GET.get('next', reverse('customer_list'))
            return redirect(next_url)

    return render(request, 'customer.html', {'form_obj': form_obj, 'edit_id': edit_id})


def consult_record_list(request, cid=0):
    """展示沟通记录"""
    if int(cid) == 0:
        query_set = ConsultRecord.objects.filter(consultant=request.user, delete_status=False)
    else:
        query_set = ConsultRecord.objects.filter(customer__id=cid, delete_status=False)
    return render(request, 'consult_record_list.html', {'consult_record_list': query_set})


def consult_record(request, edit_id=None):
    """添加与编辑沟通记录"""
    # 如果 edit_id=None 表示是新增操作，如果 edit_id 有值表示是编辑操作
    record_obj = ConsultRecord.objects.filter(pk=edit_id).first()  # 有值返回具体对象，否则返回 None
    if not record_obj:
        # 如果是添加操作，创建一个销售是我的 ConsultRecord 对象
        record_obj = ConsultRecord(consultant=request.user)

    # 使用 instance 对象的数据填充生成 input 标签
    form_obj = ConsultRecordForm(instance=record_obj, initial={'consultant': request.user})
    if request.method == 'POST':
        # 使用 POST 提交的数据去更新指定的 instance 实例
        form_obj = ConsultRecordForm(request.POST, instance=record_obj)
        if form_obj.is_valid():
            form_obj.save()
            return redirect(reverse('consult_record_list', kwargs={'cid': 0}))

    return render(request, 'consult_record.html', {'form_obj': form_obj, 'edit_id': edit_id})


def enrollment_list(request, customer_id=0):
    """查看报名表"""
    if int(customer_id) == 0:
        # 查询当前销售所有客户的报名表
        query_set = Enrollment.objects.filter(customer__consultant=request.user)
    else:
        query_set = Enrollment.objects.filter(customer_id=customer_id)
    return render(request, 'enrollment_list.html', {'enrollment_list': query_set})


def enrollment(request, customer_id=None, enrollment_id=None):
    """添加和编辑报名表"""
    # 先根据报名表id去查询
    enrollment_obj = Enrollment.objects.filter(id=enrollment_id).first()
    # 如果查询不到报名表说明是添加报名表操作
    # 又因为添加报名表必须指定客户
    if not enrollment_obj:
        enrollment_obj = Enrollment(customer=Customer.objects.filter(id=customer_id).first())

    form_obj = EnrollmentForm(instance=enrollment_obj)
    if request.method == 'POST':
        form_obj = EnrollmentForm(request.POST, instance=enrollment_obj)
        if form_obj.is_valid():
            new_obj = form_obj.save()
            # 报名成功，更改客户当前状态
            new_obj.customer.status = 'signed'
            new_obj.customer.save()  # 改的是哪张表的字段就保存哪个对象
            return redirect(reverse('enrollment_list', kwargs={'customer_id': 0}))
    return render(request, 'enrollment.html', {'form_obj': form_obj})

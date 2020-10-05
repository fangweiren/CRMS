import re
from django import forms
from django.core.exceptions import ValidationError
from crm.models import UserProfile, Customer, ConsultRecord, Enrollment


# 自定义验证规则
def mobile_validate(value):
    mobile_re = re.compile(r'^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$')
    if not mobile_re.match(value):
        raise ValidationError('手机号码格式错误')


class BootstrapBaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class RegisterForm(BootstrapBaseForm):
    # 自定义字段的那些配置不能放到 Meta 中
    re_password = forms.CharField(label='确认密码', widget=forms.widgets.PasswordInput(), )
    mobile = forms.CharField(label='手机号', validators=[mobile_validate, ])

    class Meta:
        model = UserProfile
        # fields = '__all__'  # 所有字段都展示
        fields = ['email', 'password', 're_password', 'name', 'mobile']
        labels = {
            'email': '邮箱',
            'password': '密码',
            'name': '昵称',
        }
        widgets = {
            'password': forms.widgets.PasswordInput(),
        }
        error_messages = {
            'email': {
                'required': '邮箱不能为空',
                'invalid': '邮箱输入有误'  # invalid,专门用来校验邮箱格式错误的固定用法
            },
            'password': {
                'max_length': '密码最多12位',
                'min_length': '密码最少6位',
                'required': '密码不能为空'
            },
            're_password': {
                'max_length': '确认密码最多12位',
                'min_length': '确认密码最少6位',
                'required': '确认密码不能为空'
            },
            'name': {
                'max_length': '名字最多8位',
                'min_length': '名字最少3位',
                'required': '名字不能为空'
            },
            'mobile': {
                'required': '手机号不能为空',
            },
        }

    # 校验用户名中不能含有系统（校验单个字段使用局部钩子函数）
    # 钩子函数是校验规则中最后执行的一道关卡，会先执行上面的校验规则，上面都校验通过了，才会走到钩子函数这一层的校验来。
    def clean_name(self):
        # name=self.cleaned_data 是一个校验通过的大字典
        # 通过的字典支持点get取值的方式,专门拿出来要校验的字段
        name = self.cleaned_data.get('name')
        if '系统' in name:
            # 如何给 name 所对应的框展示错误信息呢？
            # 注意下面是钩子函数的固定用法，添加对应字段的错误提示信息
            self.add_error('name', '名字中不能包含系统等字')

        # 将 name 数据返回,这个地方是必须要返回字段数据的，缺失不可
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_exist = UserProfile.objects.filter(email=email)
        if email_exist:
            raise ValidationError('邮箱已被注册')
        else:
            return email

    def clean(self):
        # 校验密码和确认密码是否一致（全局钩子函数）
        password = self.cleaned_data.get('password')
        re_password = self.cleaned_data.get('re_password')
        if not password == re_password:
            # 注意下面是钩子函数的固定用法，添加对应字段的错误提示信息
            self.add_error('re_password', '两次密码不一致')
            raise ValidationError('两次密码不一致')
        # 全局钩子是需要将全局的数据全部返回
        return self.cleaned_data


class CustomerForm(BootstrapBaseForm):
    class Meta:
        model = Customer
        fields = '__all__'

        widgets = {
            'course': forms.widgets.SelectMultiple,
            'birthday': forms.widgets.DateInput(attrs={'type': 'date'}),
        }


class ConsultRecordForm(BootstrapBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 方法一：修改字段的 choices 选项
        # self.fields['customer'].choices = Customer.objects.filter(consultant=self.instance.consultant).values_list('id', 'qq')
        # 方法二：将 form 表的字段直接修改
        self.fields['customer'] = forms.models.ModelChoiceField(
            queryset=Customer.objects.filter(consultant=self.instance.consultant).all())
        self.fields['customer'].widget.attrs.update({'class': 'form-control'})
        self.fields['consultant'].choices = [(self.instance.consultant.id, self.instance.consultant.name), ]

    class Meta:
        model = ConsultRecord
        exclude = ['delete_status', ]


class EnrollmentForm(BootstrapBaseForm):
    class Meta:
        model = Enrollment
        exclude = ['contract_approved', 'delete_status', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 限制添加报名表的时候只能选自己的私户
        self.fields['customer'].choices = [(self.instance.customer.id, self.instance.customer.name)]

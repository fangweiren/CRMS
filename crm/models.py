from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from multiselectfield import MultiSelectField

course_choices = (('Linux', 'Linux中高级'),
                  ('PythonFullStack', 'Python高级全栈开发'),
                  ('Go语言开发', 'Go高级开发'),)

class_type_choices = (('online', u'网络班'),
                      ('offline_weekend', u'面授班(周末)'),
                      ('offline_fulltime', u'面授班(脱产)'))

source_type = (('qq', u"qq群"),
               ('referral', u"内部转介绍"),
               ('website', u"官方网站"),
               ('baidu_ads', u"百度广告"),
               ('qq_class', u"腾讯课堂"),
               ('school_propaganda', u"高校宣讲"),
               ('51cto', u"51cto"),
               ('others', u"其它"))

enroll_status_choices = (('signed', "已报名"),
                         ('unregistered', "未报名"),
                         ('studying', '学习中'),
                         ('paid_in_full', "学费已交齐"))

seek_status_choices = (('A', '近期无报名计划'), ('B', '1个月内报名'), ('C', '2周内报名'), ('D', '1周内报名'),
                       ('E', '定金'), ('F', '到班'), ('G', '全款'), ('H', '无效'),)
pay_type_choices = (('deposit', "订金/报名费"),
                    ('tuition', "学费"),
                    ('transfer', "转班"),
                    ('dropout', "退学"),
                    ('refund', "退款"),)

attendance_choices = (('checked', "已签到"),
                      ('vacate', "请假"),
                      ('late', "迟到"),
                      ('absence', "缺勤"),
                      ('leave_early', "早退"),)

score_choices = ((100, 'A+'),
                 (90, 'A'),
                 (85, 'B+'),
                 (80, 'B'),
                 (75, 'B-'),
                 (70, 'C+'),
                 (60, 'C'),
                 (40, 'C-'),
                 (-50, 'D'),
                 (-1, 'N/A'),  # not avaliable
                 (-100, 'COPY'),  # 抄作业
                 )


class Customer(models.Model):
    """存储所有客户信息"""
    # 客户在咨询时，多是通过qq,所以这里就把qq号做为唯一标记客户的值，不能重复
    qq = models.CharField(verbose_name='QQ', max_length=64, unique=True, help_text=u'QQ号必须唯一')
    qq_name = models.CharField(verbose_name=u'QQ昵称', max_length=64, blank=True, null=True)
    # 客户只要没报名，你没理由要求人家必须告诉你真实姓名及其它更多私人信息呀
    name = models.CharField(verbose_name=u'姓名', max_length=32, blank=True, null=True, help_text=u'学员报名后，请改为真实姓名')
    sex_type = (('male', u'男'), ('female', u'女'))
    sex = models.CharField(verbose_name=u"性别", choices=sex_type, default='male', max_length=16, blank=True, null=True)
    birthday = models.DateField(verbose_name=u'出生日期', default=None, blank=True, null=True, help_text="格式yyyy-mm-dd")
    phone = models.BigIntegerField(verbose_name=u'手机号', blank=True, null=True)
    # phone = models.CharField(u'手机号', blank=True, null=True)
    source = models.CharField(verbose_name=u'客户来源', max_length=64, choices=source_type, default='qq')
    # 我们的很多新客户都是老学员转介绍来了，如果是转介绍的，就在这里纪录是谁介绍的他，前提这个介绍人必须是我们的老学员噢，要不然系统里找不到
    introduce_from = models.ForeignKey(to='self', verbose_name=u"转介绍自学员", blank=True, null=True)
    course = MultiSelectField(verbose_name=u'咨询课程', choices=course_choices)
    class_type = models.CharField(verbose_name=u"班级类型", max_length=64, choices=class_type_choices, default='fulltime')
    customer_note = models.TextField(verbose_name=u"客户备注", blank=True, null=True)
    status = models.CharField(verbose_name=u"状态", choices=enroll_status_choices, max_length=64, default=u"unregistered",
                              help_text=u"选择客户此时的状态")
    network_consult_note = models.TextField(blank=True, null=True, verbose_name=u'网络咨询师咨询内容')
    date = models.DateField(verbose_name=u"咨询日期", auto_now_add=True)
    last_consult_date = models.DateField(verbose_name=u'最后跟进日期', auto_now_add=True)
    next_date = models.DateField(verbose_name=u'预计再次跟进时间', blank=True, null=True)
    network_consultant = models.ForeignKey(to="UserProfile", blank=True, null=True, verbose_name=u"咨询师",
                                           related_name='network_consultant')
    consultant = models.ForeignKey(to='UserProfile', verbose_name='销售', related_name='customers', blank=True, null=True,
                                   on_delete=models.CASCADE)
    class_list = models.ManyToManyField(to='ClassList', verbose_name='已报班级', null=True,
                                        blank=True)  # null 表示数据库中可以为空，blank表示admin后台可以为空

    class Meta:
        verbose_name = '客户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}".format(self.qq, self.name)

    def show_class_list(self):
        return '|'.join([str(i) for i in self.class_list.all()])

    # 展示状态
    def show_status(self):
        _status_color = {
            'signed': 'blue',
            'unregistered': 'red',
            'studying': 'green',
            'paid_in_full': 'orange',
        }
        return mark_safe('<span style="background-color: {}; color: white">{}</span>'.format(
            _status_color[self.status],
            self.get_status_display()
        ))


class Campuses(models.Model):
    """
    校区表
    """
    name = models.CharField(verbose_name='校区', max_length=64)
    address = models.CharField(verbose_name='详细地址', max_length=512, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '校区'
        verbose_name_plural = verbose_name


class ContractTemplate(models.Model):
    """
    合同模板表
    """
    name = models.CharField("合同名称", max_length=128, unique=True)
    content = models.TextField("合同内容")
    date = models.DateField(auto_now=True)

    def __str__(self):
        return self.name


class ClassList(models.Model):
    """
    班级表
    """
    course = models.CharField("课程名称", max_length=64, choices=course_choices)
    semester = models.IntegerField("学期")  # python20期等
    campuses = models.ForeignKey('Campuses', verbose_name="校区", on_delete=models.CASCADE)
    price = models.IntegerField("学费", default=10000)
    memo = models.CharField('说明', blank=True, null=True, max_length=100)
    start_date = models.DateField("开班日期")
    graduate_date = models.DateField("结业日期", blank=True, null=True)  # 不一定什么时候结业，哈哈，所以可为空

    contract = models.ForeignKey('ContractTemplate', verbose_name="选择合同模版", blank=True, null=True,
                                 on_delete=models.CASCADE)
    teachers = models.ManyToManyField('UserProfile',
                                      verbose_name="老师")

    class_type = models.CharField(choices=class_type_choices, max_length=64, verbose_name='班级类型', blank=True,
                                  null=True)

    class Meta:
        unique_together = ("course", "semester", 'campuses')
        verbose_name = '已报课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{}-{}期({})".format(self.get_course_display(), self.semester, self.campuses)

    @staticmethod
    def list_display():
        return 'test_str'


class ConsultRecord(models.Model):
    """
    跟进记录表
    """
    customer = models.ForeignKey('Customer', verbose_name="所咨询客户", on_delete=models.CASCADE)
    note = models.TextField(verbose_name="跟进内容...")
    status = models.CharField("跟进状态", max_length=8, choices=seek_status_choices, help_text="选择客户此时的状态")
    consultant = models.ForeignKey("UserProfile", verbose_name="跟进人", related_name='records', on_delete=models.CASCADE)
    date = models.DateTimeField("跟进日期", auto_now_add=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)

    def __str__(self):
        return self.customer


class Enrollment(models.Model):
    """
    报名表
    """
    why_us = models.TextField("为什么报名", max_length=1024, default=None, blank=True, null=True)
    your_expectation = models.TextField("学完想达到的具体期望", max_length=1024, blank=True, null=True)
    contract_agreed = models.BooleanField("我已认真阅读完培训协议并同意全部协议内容", default=False)
    contract_approved = models.BooleanField("审批通过", help_text="在审阅完学员的资料无误后勾选此项,合同即生效", default=False)
    enrolled_date = models.DateTimeField(auto_now_add=True, verbose_name="报名日期")
    memo = models.TextField('备注', blank=True, null=True)
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)
    customer = models.ForeignKey('Customer', verbose_name='客户名称', on_delete=models.CASCADE)
    school = models.ForeignKey('Campuses', on_delete=models.CASCADE)
    enrolment_class = models.ForeignKey("ClassList", verbose_name="所报班级", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('enrolment_class', 'customer')

    def __str__(self):
        return self.customer.name


class PaymentRecord(models.Model):
    """
    缴费记录表
    """
    pay_type = models.CharField("费用类型", choices=pay_type_choices, max_length=64, default="deposit")
    paid_fee = models.IntegerField("费用数额", default=0)
    note = models.TextField("备注", blank=True, null=True)
    date = models.DateTimeField("交款日期", auto_now_add=True)
    course = models.CharField("课程名", choices=course_choices, max_length=64, blank=True, null=True, default='N/A')
    class_type = models.CharField("班级类型", choices=class_type_choices, max_length=64, blank=True, null=True,
                                  default='N/A')
    enrolment_class = models.ForeignKey('ClassList', verbose_name='所报班级', blank=True, null=True)
    customer = models.ForeignKey('Customer', verbose_name="客户")
    consultant = models.ForeignKey('UserProfile', verbose_name="销售")
    delete_status = models.BooleanField(verbose_name='删除状态', default=False)

    status_choices = (
        (1, '未审核'),
        (2, '已审核'),
    )
    status = models.IntegerField(verbose_name='审核', default=1, choices=status_choices)

    confirm_date = models.DateTimeField(verbose_name="确认日期", null=True, blank=True)
    confirm_user = models.ForeignKey(verbose_name="确认人", to='UserProfile', related_name='confirms', null=True,
                                     blank=True)


class CourseRecord(models.Model):
    """课程记录表"""
    day_num = models.IntegerField("节次", help_text="此处填写第几节课或第几天课程...,必须为数字")
    date = models.DateField(auto_now_add=True, verbose_name="上课日期")
    course_title = models.CharField('本节课程标题', max_length=64, blank=True, null=True)
    course_memo = models.TextField('本节课程内容', max_length=300, blank=True, null=True)
    has_homework = models.BooleanField(default=True, verbose_name="本节有作业")
    homework_title = models.CharField('本节作业标题', max_length=64, blank=True, null=True)
    homework_memo = models.TextField('作业描述', max_length=500, blank=True, null=True)
    scoring_point = models.TextField('得分点', max_length=300, blank=True, null=True)

    re_class = models.ForeignKey('ClassList', verbose_name="班级", on_delete=models.CASCADE)
    teacher = models.ForeignKey('UserProfile', verbose_name="讲师", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('re_class', 'day_num')

    def show_name(self):
        return '{}---day{}'.format(self.re_class, self.day_num)

    def __str__(self):
        return self.course_title + '\t' + str(self.day_num)


class StudyRecord(models.Model):
    """
    学习记录
    """
    attendance = models.CharField("考勤", choices=attendance_choices, default="checked", max_length=64)
    score = models.IntegerField("本节成绩", choices=score_choices, default=-1)
    homework_note = models.CharField(max_length=255, verbose_name='作业批语', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField("备注", max_length=255, blank=True, null=True)
    homework = models.FileField(verbose_name='作业文件', blank=True, null=True, default=None)
    course_record = models.ForeignKey('CourseRecord', verbose_name="某节课程", on_delete=models.CASCADE)
    student = models.ForeignKey('Customer', verbose_name="学员", on_delete=models.CASCADE)

    def __str__(self):
        return self.student.name + str(self.course_record.day_num)

    class Meta:
        unique_together = ('course_record', 'student')


class Department(models.Model):
    name = models.CharField(u'部门名称', max_length=64, blank=True, null=True)
    count = models.IntegerField('部门人数')


class UserManager(BaseUserManager):
    use_in_migration = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)  # 创建对象 UserProfile
        user.set_password(password)
        user.save(using=self._db)  # 保存到数据库
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        validators=[RegexValidator(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", '请输入正确的邮箱'), ]

    )

    name = models.CharField('名字', max_length=64)
    department = models.ForeignKey('Department', default=None, blank=True, null=True)
    mobile = models.CharField('手机号', max_length=32, default=None, blank=True, null=True)
    memo = models.TextField('备注', blank=True, null=True, default=None)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_(
        'Designates whether this user should be treated as active. '
        'Unselect this instead of deleting accounts.'
    ))
    is_superuser = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'  # 用来唯一确定auth中的用户
    REQUIRED_FIELDS = ['name']  # auth指定除了上面两个配置项的字段还有哪些字段必填

    class Meta:
        verbose_name = '账户信息'
        verbose_name_plural = '账户信息'

    def clean(self):
        super(UserProfile, self).clean()
        # 对邮件字段做校验
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        # The user is identified by their email address
        return self.name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):
        return self.name

    # 给ORM添加管理类
    objects = UserManager()

from django.db import models
from crm.models import UserProfile


# Create your models here.
class Permissions(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(max_length=32)
    is_menu = models.BooleanField(default=False)  # 是否能做菜单
    icon = models.CharField(max_length=24, null=True, blank=True)  # 菜单的图标

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 角色表
class Role(models.Model):
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField(to='Permissions', null=True, blank=True)
    user = models.ManyToManyField(to=UserProfile, related_name='roles')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

from django.db import models
from crm.models import UserProfile


class Menu(models.Model):
    title = models.CharField(verbose_name='菜单名称', max_length=32, unique=True)
    icon = models.CharField(max_length=24, null=True, blank=True)  # 菜单的图标
    weight = models.PositiveIntegerField(default=50, verbose_name='菜单权重')

    class Meta:
        verbose_name = '菜单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Permissions(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    url = models.CharField(max_length=64)
    show = models.BooleanField(default=False)  # 是否显示成菜单
    menu = models.ForeignKey(to='Menu', verbose_name='所属菜单')

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 角色表
class Role(models.Model):
    title = models.CharField(max_length=32)
    permissions = models.ManyToManyField(to='Permissions')
    user = models.ManyToManyField(to=UserProfile, related_name='roles')

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title

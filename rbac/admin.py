from django.contrib import admin
from rbac.models import Role, Permissions, Menu


# Register your models here.

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'show', 'menu']  # 控制 admin 页面显示哪些字段
    list_editable = ['url', 'show', 'menu']  # 可以直接在 admin 页面编辑的字段


class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon',]  # 控制 admin 页面显示哪些字段
    list_editable = ['icon',]  # 可以直接在 admin 页面编辑的字段

admin.site.register(Permissions, PermissionAdmin)
admin.site.register(Role)
admin.site.register(Menu, MenuAdmin)

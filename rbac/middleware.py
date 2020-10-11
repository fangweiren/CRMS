import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.shortcuts import HttpResponse


class RBACMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 1.获取当前请求的 URL
        current_url = request.path_info
        # 2.判断当前访问的URL在不在白名单中
        for url in getattr(settings, 'WHITE_URLS', []):
            if re.match(r'^{}$'.format(url), current_url):
                # 如果是白名单中的 URL 直接放行
                return

        # 判断当前这次请求的 URL 在不在权限列表里
        key = getattr(settings, 'PREMISSION_SESSION_KEY', 'permission_list')
        # 3.当前登录的这个人的权限有哪些？
        permission_list = request.session.get(key, [])
        # 4.因为 Django URL 存在模糊匹配，所以校验权限的时候要用正则
        for pattern in permission_list:
            if re.match(r'^{}$'.format(pattern), current_url):
                # 拥有权限
                return None
        else:
            return HttpResponse('没有权限')

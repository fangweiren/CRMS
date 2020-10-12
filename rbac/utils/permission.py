"""
RBAC组件
权限相关的模块
"""

from django.conf import settings


def init(request, user_obj):
    """
    根据当前登录的用户初始化权限信息和菜单信息，保存到 session 中
    :param request:请求对象
    :param user_obj:登录的用户对象
    :return:
    """
    # 将当前登录用户的权限信息查询出来
    queryset = user_obj.roles.all().filter(permissions__isnull=False).values(
        'permissions__url',  # 权限的 URL
        'permissions__title',  # 权限的名称
        'permissions__show',  # 权限是否显示
        'permissions__menu_id',  # 菜单id
        'permissions__menu__title',  # 菜单标题
        'permissions__menu__icon',  # 菜单图标
        'permissions__menu__weight',  # 菜单的权重
    ).distinct()
    # print(queryset)
    # [{
    #         'permissions__title': '客户列表',
    #         'permissions__menu__icon': 'fa-users',
    #         'permissions__menu_id': 1,
    #         'permissions__url': '/crm/customer_list/',
    #         'permissions__menu__title': '客户管理',
    #         'permissions__show': True
    #     },
    #     {
    #         'permissions__title': '我的客户',
    #         'permissions__menu__icon': 'fa-users',
    #         'permissions__menu_id': 1,
    #         'permissions__url': '/crm/my_customer/',
    #         'permissions__menu__title': '客户管理',
    #         'permissions__show': True
    #     },
    #     ...
    # ]

    # 先取到权限列表
    permission_list = []
    # 存放菜单信息的列表
    menu_dict = {}

    for item in queryset:
        permission_list.append({'url': item['permissions__url'], 'menu_id': item['permissions__menu_id']})  # 能够访问的权限列表
        # 再取出菜单列表
        p_id = item['permissions__menu_id']
        if p_id not in menu_dict:
            menu_dict[p_id] = {
                'id': p_id,
                'title': item['permissions__menu__title'],
                'icon': item['permissions__menu__icon'],
                'weight': item['permissions__menu__weight'],
                'children': [{'title': item['permissions__title'],
                              'url': item['permissions__url'],
                              'show': item['permissions__show']}]
            }
        else:
            menu_dict[p_id]['children'].append({'title': item['permissions__title'],
                                                'url': item['permissions__url'],
                                                'show': item['permissions__show']})

    # print(menu_dict)
    # {
    #     1: {
    #         'title': '客户管理',
    #         'children': [{
    #             'title': '客户列表',
    #             'url': '/crm/customer_list/'
    #         }, {
    #             'title': '我的客户',
    #             'url': '/crm/my_customer/'
    #         }, {
    #             'title': '新增客户',
    #             'url': '/crm/add/'
    #         }, {
    #             'title': '编辑客户',
    #             'url': '/crm/edit/(\\d+)/'
    #         }],
    #         'id': 1,
    #         'icon': 'fa-users'
    #     },
    #     3: {
    #         'title': '报名管理',
    #         'children': [{
    #             'title': '查看报名表',
    #             'url': '/crm/enrollment_list/(?P<customer_id>\\d+)/'
    #         }, {
    #             'title': '新增报名表',
    #             'url': '/crm/add_enrollment/(?P<customer_id>\\d+)/'
    #         }, {
    #             'title': '编辑报名表',
    #             'url': '/crm/edit_enrollment/(?P<enrollment_id>\\d+)/'
    #         }],
    #         'id': 3,
    #         'icon': 'fa-file-o'
    #     },
    # }
    # 将权限信息保存到 session 数据中
    permission_key = getattr(settings, 'PREMISSION_SESSION_KEY', 'permission_list')
    menu_key = getattr(settings, 'MENU_SESSION_KEY', 'menu_dict')
    request.session[permission_key] = permission_list
    request.session[menu_key] = menu_dict

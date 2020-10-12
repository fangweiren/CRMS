import re
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(filename='menu.html')
def show_menu(request):
    menu_key = getattr(settings, 'MENU_SESSION_KEY', 'menu_dict')
    menu_dict = request.session[menu_key]
    # menu_list = menu_dict.values()
    # 对菜单按照权重排序
    menu_list = sorted(menu_dict.values(), key=lambda x: x['weight'], reverse=True)
    for menu in menu_list:
        menu['class'] = 'hide'
        for child in menu['children']:
            if re.match(r'^{}$'.format(child['url']), request.path_info):
                child['class'] = 'active'
                menu['class'] = ''
                break
    return {'menu_list': menu_list}


@register.inclusion_tag(filename='bread_crumb.html')
def bread_crumb(request):
    bread_crumb_list = request.bread_crumb
    return {'bread_crumb_list': bread_crumb_list}

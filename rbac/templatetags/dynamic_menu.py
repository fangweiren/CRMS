import re
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(filename='menu.html')
def show_menu(request):
    menu_key = getattr(settings, 'MENU_SESSION_KEY', 'menu_list')
    menu_list = request.session[menu_key]
    for menu in menu_list:
        if re.match(r'^{}$'.format(menu['url']), request.path_info):
            menu['class'] = 'active'
            break
    return {'menu_list': menu_list}

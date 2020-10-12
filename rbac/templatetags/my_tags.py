import re
from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag(filename='menu.html')
def show_menu(request):
    menu_key = getattr(settings, 'MENU_SESSION_KEY', 'menu_dict')
    menu_dict = request.session[menu_key]
    menu_list = menu_dict.values()
    for menu in menu_list:
        for child in menu['children']:
            if re.match(r'^{}$'.format(child['url']), request.path_info):
                menu['class'] = 'active'
                break
    return {'menu_list': menu_list}

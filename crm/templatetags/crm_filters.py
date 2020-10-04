from django import template

register = template.Library()


# /crm/customer_list/?page=2
@register.filter
def replace_page(query_dict, current_page):
    query_dict['page'] = current_page
    return query_dict.urlencode()

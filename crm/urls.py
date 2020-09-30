"""
二级路由
"""
from django.conf.urls import url
from crm import views

urlpatterns = [
    url(r'customer_list/', views.customer_list, name='customer_list'),
    url(r'add/', views.add_customer, name='add_customer'),
]

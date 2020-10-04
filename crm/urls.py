"""
二级路由
"""
from django.conf.urls import url
from crm import views

urlpatterns = [
    url(r'customer_list/', views.CustomerListView.as_view(), name='customer_list'),
    url(r'my_customer/', views.CustomerListView.as_view(), name='my_customer'),
    # url(r'add/', views.add_customer, name='add_customer'),
    # url(r'edit/(\d+)', views.edit_customer, name='edit_customer'),

    #--------------新增和编辑二合一--------------------
    url(r'add/', views.customer, name='add_customer'),
    url(r'edit/(\d+)/', views.customer, name='edit_customer'),
]

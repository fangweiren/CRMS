"""
二级路由
"""
from django.conf.urls import url
from crm import views, ajax_views, class_views

urlpatterns = [
    url(r'^customer_list/$', views.CustomerListView.as_view(), name='customer_list'),
    url(r'^my_customer/$', views.CustomerListView.as_view(), name='my_customer'),
    # url(r'add/', views.add_customer, name='add_customer'),
    # url(r'edit/(\d+)', views.edit_customer, name='edit_customer'),

    # --------------新增和编辑二合一--------------------
    url(r'^add/$', views.customer, name='add_customer'),
    url(r'^edit/(\d+)/$', views.customer, name='edit_customer'),

    # 沟通记录表
    url(r'^consult_record_list/(?P<cid>\d+)/$', views.consult_record_list, name='consult_record_list'),
    url(r'^add_record/$', views.consult_record, name='add_consult_record'),
    url(r'^edit_record/(\d+)/$', views.consult_record, name='edit_consult_record'),

    # 报名表
    url(r'^enrollment_list/(?P<customer_id>\d+)/$', views.enrollment_list, name='enrollment_list'),
    url(r'^add_enrollment/(?P<customer_id>\d+)/$', views.enrollment, name='add_enrollment'),
    url(r'^edit_enrollment/(?P<enrollment_id>\d+)/$', views.enrollment, name='edit_enrollment'),

    url(r'^ajax_class/$', ajax_views.ajax_class),

    # 班级
    url(r'^class_list/$', class_views.ClassListView.as_view(), name='class_list'),
    url(r'^add_class/$', class_views.add_edit_class, name='add_class'),
    url(r'^edit_class/(?P<edit_id>\d+)$', class_views.add_edit_class, name='edit_class'),
]

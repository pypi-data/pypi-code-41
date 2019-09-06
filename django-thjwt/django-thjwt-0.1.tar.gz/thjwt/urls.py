#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2019/9/6 14:34
# @Author : tianyang@nscc-tj.gov.cn
# @About.:.
# @File : urls.py
# @Site : 
# @Software: PyCharm
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'pub/v1/access_token/$', views.get_access_token, name="access_token"),
    url(r'sso/v1/user_login_token/$', views.get_user_login_token, name="user_login_token"),
    url(r'sso/v1/user_login/$', views.user_login, name="user_login"),

    url(r'cae/v1/account/$', views.get_account_info, name="get_account_info"),
    url(r'cae/v1/users/$', views.get_users_list, name="get_users_list"),
    url(r'cae/v1/user/$', views.user_manager, name="user_manager"),
    url(r'cae/v1/jobs/account/$', views.get_accout_jobs, name="get_accout_jobs"),
    url(r'cae/v1/jobs/user/$', views.get_user_jobs, name="get_user_jobs"),
]
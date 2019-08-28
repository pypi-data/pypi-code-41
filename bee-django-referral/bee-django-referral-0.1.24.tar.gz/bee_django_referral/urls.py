#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_referral'

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.ActivityList.as_view(), name='index'),
    url(r'^activity/list$', views.ActivityList.as_view(), name='activity_list'),
    url(r'^activity/detail/(?P<pk>[0-9]+)$', views.ActivityDetail.as_view(), name='activity_detail'),
    url(r'^activity/add/$', views.ActivityCreate.as_view(), name='activity_add'),
    url(r'^activity/update/(?P<pk>[0-9]+)$', views.ActivityUpdate.as_view(), name='activity_update'),
    url(r'^activity/qrcode/upload/(?P<pk>[0-9]+)$', views.ActivityQrcodeUpload.as_view(),
        name='activity_qrcode_upload'),
    url(r'^activity/qrcode/update/(?P<pk>[0-9]+)$', views.ActivityQrcodeUpdate.as_view(),
        name='activity_qrcode_update'),
    # 二维码错误
    url(r'^activity/qrcode/invaild$', views.ActivityQrcodeInvaild.as_view(),
        name='qrcode_invaild'),  # 二维码错误页面

    # 用户活动页 - 后台
    url(r'^user/activity/add/(?P<user_id>[0-9]+)$', views.UserActivityCreate.as_view(), name="user_activity_add"),
    url(r'^user/activity/list/(?P<user_id>[0-9]+)$', views.UserActivityList.as_view(), name='user_activity_list'),
    url(r'^user/activity/delete/(?P<pk>[0-9]+)$', views.UserActivityDelete.as_view(), name='user_activity_delete'),

    # 用户活动页 - 前台
    url(r'^costom_user/activity/detail/(?P<user_id>[0-9]+)/(?P<pk>[0-9]+)$', views.UserActivityDetail.as_view(),
        name='user_activity_detail'),
    url(r'^costom_preuser/reg$', views.PreuserRegRedirectView.as_view(),
        name='preuser_reg'), # 新用户注册页跳转判断

]
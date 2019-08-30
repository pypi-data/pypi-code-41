#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views
app_name = 'bee_django_message'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.MessageList.as_view(), name='index'),
    # =======消息类型========
    url(r'^message/list/$', views.MessageList.as_view(), name='message_list'),
    url(r'^message/detail/(?P<pk>[0-9]+)/$', views.MessageDetail.as_view(), name='message_detail'),

    url(r'^message/add/$', views.MessageCreate.as_view(), name='message_add'),
    url(r'^message/update/(?P<pk>[0-9]+)/$', views.MessageUpdate.as_view(), name='message_update'),
    url(r'^message/delete/(?P<pk>[0-9]+)/$', views.MessageDelete.as_view(), name='message_delete'),



    # =======发送记录========
    url(r'^record/list/(?P<message_id>[0-9]+)/$', views.RecordList.as_view(), name='record_list'),
    url(r'^record/detail/(?P<pk>[0-9]+)/$', views.RecordDetail.as_view(), name='record_detail'),
    url(r'^record/custom/detail/(?P<pk>[0-9]+)/$', views.RecordCustomDetail.as_view(), name='record_custom_detail'),
    url(r'^record/update/(?P<pk>[0-9]+)/$', views.RecordUpdate.as_view(), name='record_update'),

    # =====发送给用户的消息======
    url(r'^custom/user/record/list/(?P<user_id>[0-9]+)/$', views.CustomUserRecordList.as_view(), name='custom_user_record_list'),
    url(r'^user/record/click/$', views.UserRecordClick.as_view(), name='user_record_click'),
    url(r'^user/record/all/click/$', views.UserRecordAllClick.as_view(), name='user_records_all_click'),

    # =======发送微信========
    # url(r'^send/wx/message/$', views.send_wx_message, name='send_wx_message'),
    # url(r'^send/email/$', views.send_email, name='send_email'),
]
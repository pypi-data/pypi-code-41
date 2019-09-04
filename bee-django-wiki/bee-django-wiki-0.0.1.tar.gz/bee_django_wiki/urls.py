#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_wiki'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.TopicList.as_view(), name='index'),
    # 分类
    url(r'^classify/list$', views.ClassifyList.as_view(), name='classify_list'),
    url(r'^classify/add$', views.ClassifyCreate.as_view(), name='classify_add'),
    url(r'^classify/update/(?P<pk>[0-9]+)$', views.ClassifyUpdate.as_view(), name='classify_update'),
    url(r'^classify/delete/(?P<pk>[0-9]+)$', views.ClassifyDelete.as_view(), name='classify_delete'),
    # 主题
    url(r'^topic/list$', views.TopicList.as_view(), name='topic_list'),
    url(r'^topic/detail/(?P<pk>[0-9]+)$', views.TopicDetail.as_view(), name='topic_detail'),
    url(r'^topic/add/$', views.TopicCreate.as_view(), name='topic_add'),
    url(r'^topic/update/(?P<pk>[0-9]+)$', views.TopicUpdate.as_view(), name='topic_update'),
    url(r'^topic/delete/(?P<pk>[0-9]+)$', views.TopicDelete.as_view(), name='topic_delete'),
    url(r'^topic/upload/image$', views.upload_image, name='upload_image'),
]

#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name = 'bee_django_coin'

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.CoinTypeList.as_view(), name='index'),
    # =======发金币类型========
    url(r'^type/list$', views.CoinTypeList.as_view(), name='coin_type_list'),
    # url(r'^message/detail/(?P<pk>[0-9]+)$', views.CoinTypeDetail.as_view(), name='coin_type_detail'),
    url(r'^type/add/$', views.CoinTypeCreate.as_view(), name='coin_type_add'),
    url(r'^type/update/(?P<pk>[0-9]+)/$', views.CoinTypeUpdate.as_view(), name='coin_type_update'),
    url(r'^type/delete/(?P<pk>[0-9]+)/$', views.CoinTypeDelete.as_view(), name='coin_type_delete'),
    # =======发送记录========
    url(r'^user/record/list/(?P<user_id>[0-9]+)/$', views.UserRecordList.as_view(), name='user_record_list'),
    url(r'^user/record/add/(?P<user_id>[0-9]+)/$', views.UserRecordCreate.as_view(), name='coin_record_add'),
    # =======其他类型金币,目前是发班级M币========
    url(r'^other/record/add/(?P<coin_identity>(.)+)/(?P<coin_content_id>[0-9]+)/$', views.OtherRecordCreate.as_view(),
        name='other_record_add'),
    url(r'^other/record/list/(?P<coin_identity>(.)+)/(?P<coin_content_id>[0-9]+)/$', views.OtherRecordList.as_view(),
        name='other_record_list'),
    # =======金币排行榜=======
    url(r'^user/rank/list/$', views.UserRankList.as_view(), name='user_rank_list'),
    url(r'^custom_user/rank/list/$', views.CustomUserRankList.as_view(), name='custom_user_rank_list'),
    # url(r'^user/record/click$', views.UserRecordClick.as_view(), name='user_record_click'),

    # =======商城=======
    # =======商品=======
    url(r'^item/list$', views.ItemList.as_view(), name='item_list'),
    url(r'^item/detail/(?P<pk>[0-9]+)$', views.ItemDetail.as_view(), name='item_detail'),
    url(r'^item/add/$', views.ItemCreate.as_view(), name='item_add'),
    url(r'^item/update/(?P<pk>[0-9]+)/$', views.ItemUpdate.as_view(), name='item_update'),
    url(r'^item/delete/(?P<pk>[0-9]+)/$', views.ItemDelete.as_view(), name='item_delete'),
    # =====用户商品======
    url(r'^item/custom/list/$', views.ItemCustomList.as_view(), name='item_custom_list'),  # 用户的商城商品列表页
    url(r'^item/custom/detail/(?P<pk>[0-9]+)/$', views.ItemCustomDetail.as_view(), name='item_custom_detail'),
    # 用户的商城商品详情页
    # =====订单======
    url(r'^order/list/$', views.OrderList.as_view(), name='order_list'),
    url(r'^order/user/list/(?P<user_id>[0-9]+)/$', views.OrderUserList.as_view(), name='order_user_list'),
    url(r'^order/custom/user/list/(?P<user_id>[0-9]+)/$', views.OrderCustomUserList.as_view(), name='order_custom_user_list'),
    url(r'^order/detail/(?P<pk>[0-9]+)/$', views.OrderDetail.as_view(), name='order_detail'),
    url(r'^order/custom/user/detail/(?P<pk>[0-9]+)/$', views.OrderCustomUserDetail.as_view(), name='order_custom_user_detail'),
    url(r'^order/add/$', views.OrderCreate.as_view(), name='order_add'),
    url(r'^order/update/status/$', views.OrderUpdateStatus.as_view(), name='order_update_status'),

]

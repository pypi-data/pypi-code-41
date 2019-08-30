#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from django import template
from django.conf import settings
from bee_django_coin.exports import filter_local_datetime,get_user_coin
from bee_django_coin.utils import get_user_name

register = template.Library()


# 本地化时间
@register.filter
def local_datetime(_datetime):
    return filter_local_datetime(_datetime)


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)

# 获取用户的M币数量
@register.filter
def get_coin(user):
    coin = get_user_coin(user)
    return coin

# 获取学生姓名，及详情链接
@register.filter
def get_name_detail(user, show_detail=True):
    if not user:
        return ''
    user_name = get_user_name(user)
    if not show_detail:
        return user_name
    if settings.USER_DETAIL_EX_LINK:
        link = "<a href='" + settings.USER_DETAIL_EX_LINK + user.id.__str__() + "/'>" + user_name + "</a>"
    else:
        link = user_name
    return link

# 获取发放金币操作人
@register.filter
def get_created_by_user_name(user):
    if not user:
        return settings.COIN_DEFAULT_NAME
    return get_name_detail(user,False)
#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from django import template
from django.conf import settings

# from bee_django_message.exports import filter_local_datetime
from bee_django_message.utils import get_user_name

register = template.Library()


# 本地化时间
# @register.filter
# def local_datetime(_datetime):
#     return filter_local_datetime(_datetime)


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)

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

@register.filter
def get_send_name(user):
    if not user:
        return settings.MESSAGE_DEFAULT_NAME
    return get_user_name(user)
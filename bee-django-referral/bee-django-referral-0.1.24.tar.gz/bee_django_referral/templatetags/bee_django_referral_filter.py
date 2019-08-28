#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template
# from bee_django_referral.exports import filter_local_datetime
from bee_django_referral.utils import get_user_name
from bee_django_referral.models import UserShareImage

register = template.Library()


# # 获取转介人姓名
# @register.filter
# def get_referral_user_name(preuser):
#     referral_user = preuser.referral_user
#     if not referral_user:
#         return None
#     return get_user_name(referral_user)



#
# # 获取自定义user的自定义name
# @register.filter
# def get_checked_user_name(user):
#     return get_user_name(user)


# 本地化时间
@register.filter
def local_datetime(_datetime):
    return _datetime


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)

# 用户姓名
@register.filter
def get_name(user):
    return get_user_name(user)


# 获取图片状态
@register.filter
def get_user_qrcode_image_status(user_qrcode_image_id):
    try:
        user_image = UserShareImage.objects.get(id=user_qrcode_image_id)
        return user_image.status
    except:
        return None
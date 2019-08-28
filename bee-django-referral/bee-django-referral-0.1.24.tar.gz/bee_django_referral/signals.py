#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.dispatch import Signal
# before_user_exam=Signal(providing_args=["user_id",'grade_id','failed',"success"])

# after_user_exam_add=Signal(providing_args=["record"])

# #注册后
# after_preuser_add=Signal(providing_args=["user", "timestamp", "preuser_id", "img_status", "activity_id"])
#
# # 缴费后
# after_preuser_pay=Signal(providing_args=["img_status","preuser_id"])
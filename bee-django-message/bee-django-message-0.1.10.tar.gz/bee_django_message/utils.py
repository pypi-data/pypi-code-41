#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import json,urllib2
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from django.http import HttpResponse

from .models import Message, SendRecord,WeixinServiceAccessToken


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


def get_message(identity=None):
    message = None
    if identity:
        try:
            message = Message.objects.get(identity=identity)
        except:
            message = None
    return message


# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, settings.USER_NAME_FIELD)
    except:
        return None





# 获取学生未读信息的数量
def get_user_new_message_count(user, message_identity=None):
    if not user or not user.is_authenticated():
        return 0
    message = get_message(message_identity)
    records = SendRecord.objects.filter(to_user=user, is_view=False)
    if message:
        records = records.filter(message=message)
    return records.count()






# context
def get_context_user_new_message_count(request):
    context = {
        'context_user_new_message_count': get_user_new_message_count(request.user),
    }
    return context

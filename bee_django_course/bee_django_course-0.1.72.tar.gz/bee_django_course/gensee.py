#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
import json
from django.utils import timezone
from django.conf import settings
from utils import http_post


# 获取直播间id
def create_room(room_name):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    create_webcast_parameters = {
        "subject": room_name.encode('utf-8'),
        "startTime": timezone.now(),
        "organizerToken": settings.GENSEE_CONFIG.student_organizerToken,
        "panelistToken": settings.GENSEE_CONFIG.student_panelistToken,
        "attendeeToken": "",
        "loginName": settings.GENSEE_CONFIG.gensee_manke_account.username,
        "password": settings.GENSEE_CONFIG.gensee_manke_account.password
    }
    create_webcast_res = gensee_api_post("/webcast/created", create_webcast_parameters)
    if create_webcast_res and create_webcast_res["code"] == "0":
        return create_webcast_res["id"]
    else:
        return None

# 删除直播间
def delete_room(room_id):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    delete_webcast_parameters = {
        "webcastId": room_id,
        "loginName": settings.GENSEE_CONFIG.gensee_manke_account.username,
        "password": settings.GENSEE_CONFIG.gensee_manke_account.password
    }
    create_webcast_res = gensee_api_post("/webcast/deleted", delete_webcast_parameters)
    if create_webcast_res and create_webcast_res["code"] == "0":
        return True
    else:
        return False


# 获取直播间信息
def get_room_info(room_id):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    live_webcast_res = gensee_api_post("/webcast/setting/info",
                                       {"webcastId": room_id, "loginName":
                                           settings.GENSEE_CONFIG.gensee_manke_account.username,
                                        "password": settings.GENSEE_CONFIG.gensee_manke_account.password})
    if live_webcast_res["code"] == "0":
        room = live_webcast_res
    else:
        room = None
    return room


def gensee_api_post(url, parameters):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    url = settings.GENSEE_CONFIG.genseeUrl + url
    res = http_post(url, parameters)
    try:
        j = json.loads(res)
    except Exception as e:
        print(e)
        j = None
    return j

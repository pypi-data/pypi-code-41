#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'bee'
import json, pytz, os, time, random
from django.conf import settings
from django.apps import apps
from django.contrib.auth.models import User
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from qr import create_qrcode, toRgb, merge_img
from .models import Activity, UserShareImage, UserShareImageRecord, UserQrcodeRecordStatus, UserActivity

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


# ====dt====
# 获取本地当前时间
# def get_now(tz=LOCAL_TIMEZONE):
#     return timezone.now()


def create_qrcode_timestamp():
    r = random.randint(1, 999)
    t = int(time.time()) * 1000 + r
    return t


def get_user_model():
    if settings.COIN_USER_TABLE in ["", None]:
        user_model = User
    else:
        app_name = settings.COIN_USER_TABLE.split(".")[0]
        model_name = settings.COIN_USER_TABLE.split(".")[1]
        app = apps.get_app_config(app_name)
        user_model = app.get_model(model_name)
    return user_model


# 获取登录用户
def get_login_user(request):
    if settings.COIN_USER_TABLE in ["", None]:
        return request.user

    token = request.COOKIES.get('cookie_token', '')
    # 没有登录
    if not token:
        return None

    try:
        user_table = get_user_model()
        user = user_table.objects.get(token=token)
        return user
    except:
        return None


# 获取用户姓名
def get_user_name(user):
    try:
        user_name = getattr(user, settings.USER_NAME_FIELD)
    except:
        user_name = user.username
    return user_name


# def save_user_qrcode_img(activity_id, user_id, timestamp, url=""):
#     try:
#         activity = Activity.objects.get(id=activity_id)
#     except:
#         return
#     qrcode_img = create_qrcode(url=url,
#                                color=activity.qrcode_color)
#     error, msg, img = merge_img(referral_base_path=activity.qrcode_bg,
#                                 qrcode_img=qrcode_img, qrcode_pos=(activity.qrcode_pos_x, activity.qrcode_pos_y),
#                                 qrcode_size=(activity.qrcode_width, activity.qrcode_height))
#     if img:
#         media_dir = os.path.join("media", 'bee_django_referral', 'qrcode')
#         if not os.path.exists(media_dir):
#             os.mkdir(media_dir)
#         media_file_path = os.path.join(media_dir,
#                                        activity.id.__str__() + "_referral_" +
#                                        user_id.__str__() + "_" + timestamp.__str__() + ".jpg")
#         output_referral_path = os.path.join(settings.BASE_DIR, media_file_path)
#         img.save(output_referral_path, quality=70)
#         return "/" + media_file_path
#     return None


# def save_user_image_db(user, activity, qrcode_path, status, timestamp):
#     user_image = UserShareImage()
#     user_image.user = user
#     user_image.activity = activity
#     user_image.qrcode = qrcode_path
#     user_image.status = status
#     user_image.timestamp = timestamp
#     user_image.save()
#     return user_image

#
# # 注册后，记录二维码状态为已使用，更新二维码记录表
# def after_preuser_add(user, timestamp, preuser_id, img_status, activity_id, **kwargs):
#     try:
#         user_image = UserShareImage.objects.get(user=user, timestamp=timestamp, activity_id=activity_id)
#     except:
#         return None
#
#     user_qrcode_record_add(user_qrcode_img_id=user_image.id, preuser_id=preuser_id,
#                            record_status=UserQrcodeRecordStatus.reg, img_status=img_status)
#
#
# # 缴费后 ，记录二维码状态为已缴费，更新二维码记录表
# def after_preuser_pay(img_status, preuser_id,**kwargs):
#     try:
#         record = UserShareImageRecord.objects.get(preuser_id=preuser_id)
#     except:
#         return
#     user_image = record.user_share_image
#     user_image.status = img_status
#     user_image.save()
#
#     user_qrcode_record_add(user_qrcode_img_id=user_image.id, preuser_id=preuser_id,
#                            record_status=UserQrcodeRecordStatus.pay, img_status=img_status)
#
#     return
#
#
# # 扫二维码[注册/成交]后，相关数据保存数据库
# def user_qrcode_record_add(user_qrcode_img_id, preuser_id, record_status, img_status):
#     try:
#         img = UserShareImage.objects.get(id=user_qrcode_img_id)
#     except:
#         return
#
#     record = UserShareImageRecord()
#     record.user_share_image = img
#     record.preuser_id = preuser_id
#     record.status = record_status
#     record.save()
#
#     if record_status in [UserQrcodeRecordStatus.reg, UserQrcodeRecordStatus.pay]:
#         img.status = img_status
#         img.save()
#         return

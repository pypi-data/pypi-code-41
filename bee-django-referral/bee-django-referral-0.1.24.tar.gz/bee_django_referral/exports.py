#!/usr/bin/env python
# -*- coding:utf-8 -*-

# from django.db.models import Q
# from .models import UserShareImage, Activity, UserShareImage, UserQrcodeRecordStatus, UserShareImageRecord
# from .utils import save_user_qrcode_img, save_user_image_db, get_now_timestamp,  get_now

__author__ = 'bee'


# django前台显示本地时间
# def filter_local_datetime(_datetime):
#     return _datetime


# 获取活动的起止时间
# def get_activity_date(activity_id):
#     try:
#         activity = Activity.objects.get(id=activity_id)
#     except:
#         return None
#     return [activity.start_date, activity.end_date]




# 生成用户二维码,并保存到数据库
# def create_user_image(user, activity_id, ex_url, status, count=3):
#     try:
#         activity = Activity.objects.get(id=activity_id)
#     except:
#         return
#
#     for i in range(0, count):
#         timestamp = get_now_timestamp()
#         url = ex_url + "&t=" + timestamp.__str__()
#         qrcode_path = save_user_qrcode_img(activity_id=activity.id, user_id=user.id, url=url, timestamp=timestamp)
#         if qrcode_path:
#             save_user_image_db(user=user, activity=activity, qrcode_path=qrcode_path, status=status,
#                                timestamp=timestamp)
#     return


# def get_user_qrcode_image(timestamp, user, activity_id):
#     try:
#         user_image = UserShareImage.objects.get(user=user, timestamp=timestamp, activity_id=activity_id)
#         return user_image
#     except:
#         return None

#
# def get_user_activity_list(user):
#     now = get_now()
#     activity_list = Activity.objects.filter(
#         Q(end_date__isnull=True) | Q(end_date__gt=now),
#         Q(start_date__isnull=True) | Q(start_date__lt=now),
#         Q(show_type=1) | Q(useractivity__user=user),
#
#     )
#     return activity_list


# def get_preuser_activity(preuser_id):
#     record_list = UserShareImageRecord.objects.filter(preuser_id=preuser_id)
#     if not record_list.exists():
#         return None
#     record = record_list.first()
#     image = record.user_share_image
#     return image.activity

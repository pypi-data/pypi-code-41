# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.dispatch import Signal
# 发送站内信的信号
send_message_signal = Signal(providing_args=["user_coin_record", 'order', 'title'])
# 记录足迹的信号
add_user_track_signal= Signal(providing_args=['order','title'])


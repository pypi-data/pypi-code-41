# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.dispatch import Signal
# 发送站内信的信号
send_message_signal = Signal(providing_args=["record"])


#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Message,SendRecord


# ===== course contract======
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['identity','name', "info",'need_done',"need_reply"]

class RecordChangeDoneForm(forms.ModelForm):
    class Meta:
        model = SendRecord
        fields = ['done_info']

class RecordSearchForm(forms.Form):
    is_done_choices =((0,"全部"),(1,"已处理"),(-1,"未处理"))
    is_done = forms.ChoiceField(choices=is_done_choices, label='', required=False)

    # class Meta:
    #     model = SendRecord
    #     fields = ['is_done']
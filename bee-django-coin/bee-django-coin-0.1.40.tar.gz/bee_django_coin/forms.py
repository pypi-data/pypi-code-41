#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from django.conf import settings
from .models import CoinType, UserCoinRecord, Item


# ===== course contract======
class CoinTypeForm(forms.ModelForm):
    class Meta:
        model = CoinType
        fields = ['name', "identity", "coin", "info"]


class UserCoinRecordForm(forms.ModelForm):
    class Meta:
        model = UserCoinRecord
        fields = ["coin", "reason", 'coin_type']


class OtherCoinCreateForm(forms.ModelForm):
    user = forms.ModelChoiceField(label='选择学生', required=True, queryset=None)
    coin = forms.IntegerField(label='数量', required=True, min_value=1)
    reason = forms.CharField(label='原因', required=False)

    class Meta:
        model = UserCoinRecord
        fields = ["user", "coin", "reason"]

    def __init__(self, users, *args, **kwargs):
        super(OtherCoinCreateForm, self).__init__(*args, **kwargs)
        self.fields["user"] = forms.ModelChoiceField(queryset=users, label='选择学生', required=True)

#
class ItemForm(forms.ModelForm):
    ITEM_TYPE_CHOICES = ((2, "抵用券"),)
    coin = forms.IntegerField(label='商品价格',help_text='购买所需'+settings.COIN_NAME,required=True,min_value=1)
    item_type = forms.ChoiceField(choices=ITEM_TYPE_CHOICES, label='商品类型')
    # stauts=forms.ChoiceField(label='商品状态',choices=ITEM_STATUS)

    class Meta:
        model = Item
        fields = ["name","url", "coin", 'pic', 'item_type', 'status', "info"]

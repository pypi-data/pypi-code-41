# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import Activity, UserActivity
from .validators import jpg_validator


# ===source===
class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'link_name','link', 'source_id', 'show_type', 'start_date', 'end_date', 'detail', 'info', "explain"]


class ActivityUpdateForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['name', 'link_name','link', 'source_id', 'show_type', 'start_date', 'end_date', 'detail', 'info', "explain"]


class ActivityQrCodeImgUpdateForm(forms.ModelForm):
    qrcode_bg = forms.ImageField(validators=[jpg_validator],label='二维码图片',required=True)

    class Meta:
        model = Activity
        fields = ['qrcode_bg']


class ActivityQrCodeUpdateForm(forms.ModelForm):
    qrcode_width = forms.IntegerField(min_value=1, label='二维码宽度', required=False)
    qrcode_height = forms.IntegerField(min_value=1, label='二维码高度', required=False)

    class Meta:
        model = Activity
        fields = ["qrcode_width", "qrcode_height", "qrcode_pos_x", "qrcode_pos_y", "qrcode_color", ]


class UserActivityForm(forms.ModelForm):
    activity = forms.ModelChoiceField(queryset=Activity.objects.filter(show_type=2), label='活动', required=True)

    class Meta:
        model = UserActivity
        fields = ["activity"]

        # def validate_unique(self):
        #     exclude = self._get_validation_exclusions()
        #     # exclude.remove('level') # allow checking against the missing attribute
        #
        #     try:
        #         self.instance.validate_unique(exclude=exclude)
        #     except forms.ValidationError, e:
        #         self._update_errors(e.message_dict)

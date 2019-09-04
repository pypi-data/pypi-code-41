# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from django.contrib.auth.models import Group
from .models import Classify, Topic,TopicImage


class ClassifyForm(forms.ModelForm):
    class Meta:
        model = Classify
        fields = ['name']


class TopicForm(forms.ModelForm):
    # view_group = forms.ModelChoiceField(queryset=Group.objects.all(), label='可观看用户组', required=False)
    class Meta:
        model = Topic
        fields = ["classify", "title", "view_group", 'tag', "detail"]


class TopicSearchForm(forms.Form):
    name = forms.CharField(label='', required=False, widget=forms.TextInput(attrs={'placeholder': '输入标题或标签进行搜索','style':'width:50%;height:34px;'}))

class TopicImageForm(forms.ModelForm):
    class Meta:
        model = TopicImage
        fields = ["image"]
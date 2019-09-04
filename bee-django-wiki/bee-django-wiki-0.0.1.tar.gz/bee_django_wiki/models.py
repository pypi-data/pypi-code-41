# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import Group

# Create your models here.
class Classify(models.Model):
    name = models.CharField(max_length=180, verbose_name='分类')

    class Meta:
        app_label = 'bee_django_wiki'
        db_table = 'bee_django_wiki_classify'
        permissions = (
            ('view_all_classify', '可以查看分类'),
        )

    def __unicode__(self):
        return self.name


class Topic(models.Model):
    title = models.CharField(max_length=180, verbose_name='标题')
    detail = models.TextField(verbose_name='详情')
    tag = models.CharField(max_length=180, verbose_name='标签', null=True, blank=True)
    classify = models.ForeignKey(Classify, verbose_name='分类', null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_by = models.IntegerField(null=True, verbose_name='排序', default=0)
    # view_group = models.TextField(verbose_name='可观看的用户组', null=True)  # group id，开头结尾和中间用|分割，例如|1|2|
    view_group = models.ManyToManyField(Group,verbose_name='可观看的用户组（可多选）')
    class Meta:
        app_label = 'bee_django_wiki'
        db_table = 'bee_django_wiki_topic'
        ordering = ["-updated_at"]
        permissions = (
            ('view_all_topic', '查看所有主题'),  # 无视view_group
        )

    def __unicode__(self):
        return self.title


class TopicImage(models.Model):
    image = models.ImageField(verbose_name='图片', upload_to='wiki/%Y/%m/%d')
    class Meta:
        app_label = 'bee_django_wiki'
        db_table = 'bee_django_wiki_toipc_image'
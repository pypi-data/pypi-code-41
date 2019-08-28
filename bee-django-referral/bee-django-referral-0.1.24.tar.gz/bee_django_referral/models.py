# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os, time, random
from django.db import models, transaction
from django.core.urlresolvers import reverse
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from .qr import create_qrcode as qr_create_qrcode
from .qr import merge_img as qr_merge_img

ACTIVITY_SHOW_TYPE_CHOICES = ((1, '全部显示'), (2, "指定用户显示"))


class Activity(models.Model):
    name = models.CharField(max_length=180, verbose_name='活动名称')
    link_name = models.CharField(max_length=180, verbose_name='链接文字')
    link = models.URLField(max_length=180, verbose_name='跳转链接', help_text='填写此字段后，点击后将直接进入第三方页面', null=True, blank=True)
    source_id = models.IntegerField(null=True, blank=True, verbose_name='渠道id', help_text='crm中对应渠道id')
    source_name = models.CharField(max_length=180, verbose_name='渠道名称', null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='开始时间', help_text='格式：2000-01-01 00:00:00')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='结束时间', help_text='格式：2000-01-01 00:00:00')
    detail = models.TextField(verbose_name='活动说明', null=True, blank=True)
    info = models.TextField(verbose_name='分享说明', null=True, blank=True)
    show_type = models.IntegerField(verbose_name='显示类型', choices=ACTIVITY_SHOW_TYPE_CHOICES, default=1)
    explain = models.TextField(verbose_name='规则解释', null=True, blank=True)
    # ===二维码===
    qrcode_width = models.IntegerField(verbose_name='二维码宽度', null=True, blank=True, default=0)
    qrcode_height = models.IntegerField(verbose_name='二维码高度', null=True, blank=True, default=0)
    qrcode_pos_x = models.IntegerField(verbose_name='二维码x轴坐标', null=True, blank=True, default=0)
    qrcode_pos_y = models.IntegerField(verbose_name='二维码y轴坐标', null=True, blank=True, default=0)
    qrcode_color = models.CharField(max_length=8, verbose_name='二维码颜色', default='#000000', null=True)
    qrcode_bg = models.ImageField(verbose_name='二维码',
                                  upload_to='bee_django_referral/qrcode/bg', null=True,
                                  blank=True)
    qrcode_thumb = models.CharField(verbose_name='二维码预览图', max_length=180, null=True, blank=True)
    qrcode_url = models.CharField(verbose_name='二维码地址', max_length=180, null=True, blank=True)

    class Meta:
        db_table = 'bee_django_referral_activity'
        app_label = 'bee_django_referral'
        permissions = (
            ('can_manage_referral', '可以进入转介活动管理页'),
        )

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_referral:activity_detail', kwargs={"pk": self.id.__str__()})

    def get_show_type(self):
        if self.show_type == 1:
            return '全部显示'
        if self.show_type == 2:
            return '指定用户显示'

    @classmethod
    def get_activity_list(cls, user):
        now = timezone.now()

        activity_list = cls.objects.filter(
            Q(end_date__isnull=True) | Q(end_date__gt=now),
            Q(start_date__isnull=True) | Q(start_date__lt=now),
            Q(show_type=1) | Q(useractivity__user=user),

        )
        return activity_list

    # 创建二维码图片
    def create_qrcode_img(self, qrcode_id=None, user_id=None, timestamp=None):
        url = settings.REFERRAL_QRCODE_PRE_URL
        if qrcode_id:
            url += '?qid=' + qrcode_id.__str__()
        qrcode_img = qr_create_qrcode(url=url,
                                      color=self.qrcode_color)
        error, msg, img = qr_merge_img(referral_base_path=self.qrcode_bg,
                                       qrcode_img=qrcode_img,
                                       qrcode_pos=(self.qrcode_pos_x, self.qrcode_pos_y),
                                       qrcode_size=(self.qrcode_width, self.qrcode_height))
        if not img:
            return
        media_dir = os.path.join("media", 'bee_django_referral', 'qrcode')
        if not os.path.exists(media_dir):
            os.mkdir(media_dir)
        if not user_id:
            user_id = ''
        if not timestamp:
            timestamp = ''
        media_file_path = os.path.join(media_dir,
                                       self.id.__str__() + "_referral_" +
                                       user_id.__str__() + "_" + timestamp.__str__() + ".jpg")
        output_referral_path = os.path.join(settings.BASE_DIR, media_file_path)
        img.save(output_referral_path, quality=70)
        return "/" + media_file_path


IMAGE_QRCODE_STATUS = ((1, '未使用'), (2, '已注册'), (4, '已缴费'))


class UserShareImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    qrcode = models.ImageField(verbose_name='二维码', upload_to='bee_django_referral/user_qrcode/', null=True)
    created_at = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)
    status = models.IntegerField(default=0, choices=IMAGE_QRCODE_STATUS, verbose_name='状态')
    timestamp = models.BigIntegerField(default=0, verbose_name='时间戳')

    class Meta:
        db_table = 'bee_django_referral_image'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.id.__str__()

    @classmethod
    @transaction.atomic
    def add_qrcode(cls, activity, user, count=1):
        if not hasattr(settings, "REFERRAL_QRCODE_PRE_URL"):
            return

        for i in range(0, count):
            # 数据库中先创建一条记录
            timestamp = int(time.time()) * 1000 + random.randint(1, 999)
            user_image = UserShareImage()
            user_image.user = user
            user_image.activity = activity
            user_image.status = 1
            user_image.timestamp = timestamp
            # 创建二维码图片
            qrcode_path = activity.create_qrcode_img(user_image.id, user.id, timestamp)

            # 保存到数据库
            user_image.qrcode = qrcode_path
            user_image.save()
        return True

    def change_qrcode_status(self, _type, preuser_id):
        print ('1111')
        print (preuser_id)
        if _type == 'reg':
            self.status = 2
        elif _type == 'fee':
            self.status = 4
        else:
            return
        self.save()
        UserShareImageRecord().add_record(self.id, preuser_id, _type)
        return

    def is_qrcode_unused(self):
        if self.status == 1:
            return True
        return False

    def is_qrcode_reg(self):
        if self.status == 2:
            return True
        return False

    def is_qrcode_fee(self):
        if self.status == 3:
            return True
        return False

    # 获取用户的二维码图片
    @classmethod
    def get_user_qrcode(cls, user, activity_id, status=None):
        image_list = cls.objects.filter(user=user, activity__id=activity_id)
        if status:
            image_list = image_list.filter(status__in=status)
        return image_list

    @classmethod
    def check_qrcode_valid(cls, id):
        try:
            qrcode = cls.objects.get(pk=id)
        except:
            return None, 4
        if qrcode:
            if not qrcode.is_qrcode_unused():
                return None, 1
        now = timezone.now()
        if now < qrcode.activity.start_date:
            return None, 2
        elif qrcode.activity.end_date < now:
            return None, 3
        return qrcode, 0

    @classmethod
    def get_qrcode_errmsg(cls, errcode):
        errcode=int(errcode)
        errmsg_list = ['', '此二维码已被使用过', '活动未开始', '活动已结束', '二维码错误']
        if errcode in [1, 2, 3, 4]:
            return errmsg_list[errcode]
        return '未知错误'

    @classmethod
    def fix_qrcode(cls):
        for q in cls.objects.filter(status=1):
            qid = q.id
            user_id = q.user.id
            timestamp = q.timestamp
            print(qid, user_id, timestamp)
            qrcode_path = q.activity.create_qrcode_img(qid, user_id, timestamp)
            # 保存到数据库
            q.qrcode = qrcode_path
            q.save()
        return


class UserQrcodeRecordStatus:
    reg = 1
    pay = 2


class UserShareImageRecord(models.Model):
    user_share_image = models.ForeignKey(UserShareImage)
    preuser_id = models.IntegerField(verbose_name='crm中preuser的id')
    status = models.IntegerField(default=0, verbose_name='状态')
    created_at = models.DateTimeField(verbose_name='时间', auto_now_add=True)

    class Meta:
        db_table = 'bee_django_referral_record'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.user_share_image.qrcode + ',status:' + self.status.__str__()

    @classmethod
    def add_record(cls, qid, preuser_id, status_type):
        try:
            qrcode = UserShareImage.objects.get(id=qid)
        except:
            return
        if status_type == 'reg':
            status = 1
        elif status_type == 'pay':
            status = 2
        else:
            return
        record = UserShareImageRecord()
        record.user_share_image = qrcode
        record.preuser_id = preuser_id
        record.status = status
        record.save()

        return

    @classmethod
    def get_qrcode_image(cls, preuser_id):
        record_list = cls.objects.filter(preuser_id=preuser_id)
        if not record_list.exists():
            return None
        record = record_list.first()
        return record.user_share_image


class UserActivity(models.Model):
    activity = models.ForeignKey(Activity, verbose_name='转介活动')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = 'bee_django_referral_user_activity'
        app_label = 'bee_django_referral'
        unique_together = ("activity", "user")
        permissions = (
            ('view_user_activity', '可以查看学生转介活动'),
        )

    def __unicode__(self):
        return self.user + ',activity:' + self.activity.name

    @classmethod
    def get_user_activity_list(cls, user):
        now = timezone.now()
        user_activity_list = cls.objects.filter(
            Q(activity__end_date__isnull=True) | Q(activity__end_date__gt=now),
            Q(activity__start_date__isnull=True) | Q(activity__start_date__lt=now),
            Q(activity__show_type=1) | Q(user=user),

        )
        return user_activity_list

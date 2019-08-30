# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime, pytz
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.dispatch import receiver
from django.db.models.signals import post_save
from .signals import send_message_signal, add_user_track_signal

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


# Create your models here.
def get_user_table():
    return settings.AUTH_USER_MODEL


# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, settings.USER_NAME_FIELD)
    except:
        return None


class CoinType(models.Model):
    name = models.CharField(max_length=180, verbose_name='名称类型')
    coin = models.IntegerField(verbose_name="数量")
    info = models.CharField(max_length=180, null=True, blank=True, verbose_name='说明')
    identity = models.CharField(max_length=180, null=True, verbose_name='标识符', unique=True, help_text='此字段唯一')

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_type'
        ordering = ["id"]
        permissions = (
            ('can_manage_coin', '可以进入M币管理页'),
        )

    def __unicode__(self):
        return (self.name)

    def get_absolute_url(self):
        return reverse('bee_django_coin:coin_type_list')


# 缦币
class UserCoinRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='coin_user')
    coin = models.IntegerField(verbose_name='数量', help_text='扣除填入负数')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_by_user", null=True)
    reason = models.CharField(max_length=180, verbose_name='原因', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    coin_type = models.ForeignKey('bee_django_coin.CoinType', null=True, on_delete=models.SET_NULL, verbose_name='类型')
    coin_content_id = models.IntegerField(null=True)  # 如果coin_type为班级金币，此字段为班级id

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_record'
        ordering = ["-created_at"]

    def __unicode__(self):
        return ("UserCoinRecord->reason:" + self.reason)

    def get_absolute_url(self):
        return reverse('bee_django_coin:user_record_list', kwargs={"user_id": self.user.id})

    def get_created_by_user_name(self):
        if self.created_by:
            return get_user_name(self.created_by)
        else:
            return settings.COIN_DEFAULT_NAME


class UserCoinCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    coin_count = models.IntegerField(default=0)

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_rank_list'
        ordering = ["-coin_count"]

    def __unicode__(self):
        return ("UserCoinCount->user:" + self.coin_count.__str__())

    @classmethod
    def update(cls, user):
        user_record = UserCoinRecord.objects.filter(user=user).aggregate(sum_coin=Sum("coin"))
        try:
            user_count = cls.objects.get(user=user)
        except:
            user_count = cls()
            user_count.user = user
        user_count.coin_count = user_record["sum_coin"]
        user_count.save()

        return


# 增加记录后，
# 1.自动更新用户总M币数量
# 2.如果发的是班级m币，自动扣减班级m币总数
@receiver(post_save, sender=UserCoinRecord)
def create_user(sender, **kwargs):
    user_record = kwargs['instance']
    if kwargs['created']:
        send_message_signal.send(sender=UserCoinRecord, user_coin_record=user_record)
        UserCoinCount.update(user_record.user)
        # 更新班级M币总数
        if user_record.coin_type.identity == 'user_class':
            OtherCoinCount.update(coin_type=user_record.coin_type, coin_content_id=user_record.coin_content_id,
                                  count=user_record.coin)
    return


# OTHER_TYPE_CHOICES = ((1, "班级剩余金币"),)


class OtherCoinCount(models.Model):
    # other_type = models.CharField(max_length=180, choices=OTHER_TYPE_CHOICES, null=True)
    coin_type = models.ForeignKey('bee_django_coin.CoinType', null=True, on_delete=models.SET_NULL, verbose_name='类型')
    coin_content_id = models.IntegerField()  # other_type为班级剩余金币，此字段为班级id
    count = models.IntegerField(default=0)  # 金币数
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_other_count'
        ordering = ["pk"]
        permissions = (
            ('add_teach_class_coin', '可以发所教班级M币'),
        )

    def __unicode__(self):
        return (
            "OtherCoinCount->other_type:" + self.coin_type.name + ",other_type_id:" + self.other_type_id.__str__())

    # 更新M币总数
    @classmethod
    def update(cls, coin_type, coin_content_id, count):
        records = cls.objects.filter(coin_type=coin_type, coin_content_id=coin_content_id)
        if not records.exists():
            return
        record = records.first()
        new_coin = record.count - count
        record.count = new_coin
        record.save()


# ======商城
# 商品
ITEM_TYPE_CHOICES = ((1, "实物"), (2, "抵用券"))
ITEM_STATUS_CHOICES = ((1, "上架"), (2, "下架"))


class Item(models.Model):
    name = models.CharField(max_length=180, verbose_name='商品名称')  # 商品名
    coin = models.IntegerField(verbose_name='购买需要')  # 缦币
    pic = models.ImageField(null=True, blank=True, verbose_name="商品图片", upload_to='bee_django_coin/shop/item')  # 商品图片
    info = models.TextField(null=True, verbose_name='详情', blank=True)  # 详情
    item_type = models.IntegerField(default=0, verbose_name='商品类型', choices=ITEM_TYPE_CHOICES)  # 商品类型 1-实物 2-虚拟
    status = models.IntegerField(default=0, verbose_name="商品状态", choices=ITEM_STATUS_CHOICES)  # 商品状态 1-正常显示，即上架的，2-下架的
    edit_at = models.DateTimeField(auto_now=True)  # 修改时间
    url = models.URLField(null=True,blank=True,verbose_name='商品链接',help_text='填写此项后，点击该商品则自动跳转到链接地址。')

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_item'
        ordering = ["pk"]
        permissions = (
            ('view_item_list', '查看商品列表'),
        )

    def __unicode__(self):
        return ("Item->name:" + self.name)

    def get_absolute_url(self):
        return reverse('bee_django_coin:item_list')

    def get_pic_url(self):
        if not self.pic:
            return '/static/bee_django_coin/img/shop/default_item.jpg'
        return self.pic.url

    def get_seled_count(self):
        total_count = 0
        orders = Order.objects.filter(item_id=self.id, ).aggregate(Sum('item_count'))
        if orders["item_count__sum"]:
            total_count = orders["item_count__sum"]
        return total_count

    def get_status(self):
        if not self.status:
            return ""
        for g in ITEM_STATUS_CHOICES:
            if self.status == g[0]:
                return g[1]
        return ""

    def get_item_type(self):
        if not self.item_type:
            return ""
        for g in ITEM_TYPE_CHOICES:
            if self.item_type == g[0]:
                return g[1]
        return ""


# 订单
ORDER_STATUS_CHOICES = ((1, "待付款"), (2, "已付款"), (3, "已使用完成"), (4, '已退款'))


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='购买人')  # 购买人
    # item = models.ForeignKey('shop.Item', related_name='shop_order_item')  # 购买的商品
    order_id = models.CharField(max_length=180)  # 订单长id 时间+3位随机数+userid
    item_id = models.IntegerField()  # 商品id
    item_name = models.CharField(max_length=180)  # 购买的商品名称
    item_count = models.IntegerField(default=0)  # 购买的商品数量
    item_coin = models.IntegerField(default=0)  # 购买的商品总价格
    created_at = models.DateTimeField(auto_now_add=True)  # 订单产生时间
    status = models.IntegerField(default=1)  # 状态
    info = models.TextField(null=True, verbose_name='备注')  # 备注信息
    evaluate = models.IntegerField(null=True)  # 评价 1好评 -1差评 0中评
    evaluate_info = models.TextField(null=True)  # 评价详情
    evaluate_datetime = models.DateTimeField(null=True)  # 评价时间，已此来判断是否评价

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_order'
        ordering = ["-created_at"]
        permissions=(
            ('view_order_list', '查看订单列表'),
        )

    def __unicode__(self):
        return ("Order->name:" + self.item_name)

    def get_status(self):
        if not self.status:
            return ""
        for g in ORDER_STATUS_CHOICES:
            if self.status == g[0]:
                return g[1]
        return ""

    # 不检查，直接更改订单状态，及详情
    # 发送站内信
    def change_status_info(self, op_user, status=1):
        info_type = '下单成功'
        # 支付
        if status in [2, "2"]:
            if not self.status == 1:
                return (1, '订单状态错误')

            self.status = 2
            self.save()
            info_type = '支付成功'

        # 消费
        if status in [3, "3"]:
            if not self.status == 2:
                return (1, '订单状态错误')
            info_type = '消费完成'
        self.status = status
        now = datetime.datetime.now(tz=LOCAL_TIMEZONE)
        if not self.info:
            info = ""
        else:
            info = self.info
        info += "<p>由【" + get_user_name(op_user) + "】于" + now.strftime("%Y-%m-%d %H:%M:%S") + info_type + "<p>"
        self.info = info
        self.save()
        # 发站内信，记录足迹
        if self.status in [2, "2"]:
            title = '购买商品:' + self.item_name
            add_user_track_signal.send(sender=Order, title=title, order=self)

        elif self.status in [3, "3"]:
            title = '购买的商品:' + self.item_name + "已消费完成"
            send_message_signal.send(sender=Order, title=title, order=self)
            add_user_track_signal.send(sender=Order, title=title, order=self)
        return (0, info_type)

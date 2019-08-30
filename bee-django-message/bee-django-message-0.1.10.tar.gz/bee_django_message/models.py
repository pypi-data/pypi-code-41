#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import urllib2, json, datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives


# Create your models here.
# def get_user_table():
#     return settings.AUTH_USER_MODEL


# 站内信
class Message(models.Model):
    name = models.CharField(max_length=180, verbose_name='消息名称')
    info = models.CharField(max_length=180, null=True, blank=True, verbose_name='说明')
    need_done = models.BooleanField(default=False, verbose_name='是否需要后台处理', help_text='如果不需后台显示，则不用填写')
    need_reply = models.BooleanField(default=False, verbose_name='后台处理后是否回复', help_text='如果不需处理，则不用填写')
    identity = models.CharField(max_length=180, null=True, verbose_name='标识符', unique=True, help_text='此字段唯一')

    class Meta:
        app_label = 'bee_django_message'
        db_table = 'bee_django_message'
        ordering = ["id"]

    def __unicode__(self):
        return ("Message->name:" + self.name)

    def get_absolute_url(self):
        return reverse('bee_django_message:message_list')

    def get_done(self):
        if self.need_done:
            return "是"
        else:
            return '否'

    def get_replay(self):
        if self.need_reply:
            return "是"
        else:
            return '否'


# 站内信
class SendRecord(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bee_message_from_user', verbose_name='来自',
                                  null=True)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bee_message_to_user', verbose_name='发送给',
                                null=True)
    message = models.ForeignKey('bee_django_message.Message', related_name='record_message', null=True)
    title = models.CharField(max_length=180, verbose_name='主题')
    info = models.CharField(max_length=180, null=True, verbose_name='内容', blank=True)
    is_view = models.BooleanField(default=False, verbose_name='是否看过')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='发送时间')
    url = models.CharField(max_length=180, null=True, verbose_name='点击后跳转到的页面')
    is_done = models.BooleanField(default=False, verbose_name='是否处理过')
    done_info = models.TextField(verbose_name='处理结果', null=True, blank=True, help_text='如设置为【发送回执】，填写后会给发送人发站内信')
    done_at = models.DateTimeField(null=True)
    done_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='done_by_user', null=True)

    class Meta:
        app_label = 'bee_django_message'
        db_table = 'bee_django_message_record'
        ordering = ["-sent_at"]
        permissions = (("view_message_records", "Can view message records"),)

    def __unicode__(self):
        return ("SendRecord->title:" + self.title)

    def get_absolute_url(self):
        return reverse('bee_django_message:record_list')

    def get_reply_title(self):
        return u'您发送的提醒已受理：' + self.done_info

    def get_reply_info(self):
        return None

    def get_reply_url(self):
        return reverse("bee_django_message:record_custom_detail", kwargs={"pk": self.pk})

    @classmethod
    def send_message(cls,from_user=None, to_user=None, message_identity=None, title="", info="", url=""):
        message = None
        if message_identity:
            try:
                message = Message.objects.get(identity=message_identity)
            except:
                message = None
        try:
            record = cls()
            record.from_user = from_user
            record.to_user = to_user
            record.message = message
            record.title = title
            record.info = info
            record.url = url
            record.save()
            return True
        except Exception as e:
            print('bee_django_message->send_message->error:' + e.__str__())
            return False

# 邮件
class EmailMessage(models.Model):
    name = models.CharField(max_length=180, verbose_name='消息名称')
    to_user = models.TextField(verbose_name="发送给", help_text='发送给多人时，用；隔离开', null=True)
    title = models.CharField(max_length=180, verbose_name='邮件标题')
    info = models.CharField(max_length=180, null=True, blank=True, verbose_name='说明')
    identity = models.CharField(max_length=180, verbose_name='标识符', unique=True, help_text='此字段唯一')

    class Meta:
        app_label = 'bee_django_message'
        db_table = 'bee_django_message_email'
        ordering = ["id"]

    def __unicode__(self):
        return ("EmailMessage->name:" + self.name)


# 邮件
class EmailSendRecord(models.Model):
    email_message = models.ForeignKey('bee_django_message.EmailMessage', related_name='email_message')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='email_send_record_user', null=True)
    title = models.CharField(max_length=180, null=True)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'bee_django_message'
        db_table = 'bee_django_message_email_record'
        ordering = ["-created_at"]

    def __unicode__(self):
        return ("EmailSendRecord->to_user:" + self.to_user)

    @classmethod
    def get_course_notify_context(cls, ucs):
        if not hasattr(settings, "EMAIL_CONFIG"):
            return None, 'settings没有配置'
        try:
            email_message = EmailMessage.objects.get(identity='course_notify')
        except:
            return None, '没有符合的EmailMessage'
        user = ucs.user
        html_context = "<p>" + email_message.title
        html_context += "<p>缦客：" + user.get_sn() + user.get_user_name()

        assistant = user.get_assistant()
        if assistant:
            html_context += "<p>助教：" + assistant.get_sn().__str__() + assistant.get_user_name()
        html_context += "<p>课程：" + ucs.user_course.course.name
        html_context += "<p>课件：" + ucs.section.name
        html_context += "<p>要求时间：" + (ucs.section.video_length_req + ucs.teacher_add_mins).__str__() + "分钟"
        html_context += "<p>练习时间：" + (ucs.work_time - ucs.minus_mins).__str__() + "分钟"
        # html_context += "<p><a href='http://manxuetang.com/course/editUserCourseSection?id=" + user.id.__str__() + "&user_course_id=" + us.user_course.id.__str__() + "'>前往（需登录）</a><p>"
        return html_context, '成功'

    @classmethod
    def send_course_notify_email(cls, ucs):
        if not hasattr(settings, "EMAIL_CONFIG"):
            return None, 'settings没有配置'
        try:
            email_message = EmailMessage.objects.get(identity='course_notify')
        except:
            return None, '没有符合的EmailMessage'
        to_mail_list = ";".split(email_message.to_user)
        if len(to_mail_list) < 1:
            return False
        try:
            form_email = settings.EMAIL_CONFIG.host_user
            subject = settings.EMAIL_CONFIG.subject_prefix + email_message.title
            html_content = cls().get_course_notify_context(ucs)
            msg = EmailMultiAlternatives(subject, email_message.title, form_email, to_mail_list)
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
            record = cls()
            record.email_message = email_message
            record.title = subject
            record.content = html_content
            record.save()
        except Exception as e:
            print("=" * 10 + "send_email:" + e.__str__())
            return None,'错误'



# 微信
class WeixinService(models.Model):
    class Meta:
        db_table = 'bee_django_message'
        app_label = 'bee_django_message_weixin_service'

    @classmethod
    def send_wx_message(cls, template_identity, openId, first=None, keyword1=None, keyword2=None, keyword3=None,
                        keyword4=None, keyword5=None, remark=None, url=None):
        if not hasattr(settings, "WEIXIN_SERVICE_CONFIG"):
            return
        wx_template_obj = settings.WEIXIN_SERVICE_CONFIG.WeixinService.Template
        if template_identity == 'course_notify_assistant':
            template_id = wx_template_obj.course_up_req
        elif template_identity == 'course_pass':
            template_id = wx_template_obj.course_pass
        else:
            return
        token = WeixinServiceAccessToken().get_token()
        # print(token)
        weixinUrl = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=" + token
        data = json.dumps({"touser": openId,
                           "template_id": template_id,
                           "url": url,
                           "topcolor": "#FF0000",
                           "data": {
                               "first": {
                                   "value": first,
                                   "color": "#173177"
                               },
                               "keyword1": {
                                   "value": keyword1,
                                   "color": "#173177"
                               },
                               "keyword2": {
                                   "value": keyword2,
                                   "color": "#173177"
                               },
                               "keyword3": {
                                   "value": keyword3,
                                   "color": "#173177"
                               },
                               "keyword4": {
                                   "value": keyword4,
                                   "color": "#173177"
                               },
                               "keyword5": {
                                   "value": keyword5,
                                   "color": "#173177"
                               },
                               "remark": {
                                   "value": remark,  # "请安排好时间",
                                   "color": "#FF0000"
                               }
                           }
                           })
        # print(data)
        req = urllib2.urlopen(weixinUrl, data)
        res = req.read()
        # print('=========================')
        # print(res)
        return json.loads(res)


class WeixinServiceAccessToken(models.Model):
    token = models.CharField(max_length=180)
    appid = models.CharField(max_length=180)
    appsecrect = models.CharField(max_length=180)
    alias = models.CharField(max_length=180)
    expires = models.IntegerField()
    gettime = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'bee_django_message'
        db_table = 'bee_django_message_weixin_service_access_token'

    def __unicode__(self):
        return self.token

    @classmethod
    def create_token(cls):
        if not hasattr(settings, "WEIXIN_SERVICE_CONFIG"):
            return None
        appid = settings.WEIXIN_SERVICE_CONFIG.appid
        app_secret = settings.WEIXIN_SERVICE_CONFIG.app_secret
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid + "&secret=" + app_secret
        res = urllib2.urlopen(url).read()
        obj = json.loads(res)
        # 保存
        t = cls()
        t.token = obj["access_token"]
        t.expires = obj["expires_in"]
        t.gettime = timezone.now()
        t.appid = appid
        t.appsecrect = app_secret
        t.save()
        return t

    @classmethod
    def get_token(cls):
        tokens = cls.objects.all().order_by("-gettime")
        if not tokens.exists():
            t = cls.create_token()
            return t.token

        old_token = tokens.first()
        expire_dt = old_token.gettime + datetime.timedelta(seconds=old_token.expires)
        if old_token.token and timezone.now() < expire_dt:
            return old_token.token
        else:
            t = cls.create_token()
            return t.token

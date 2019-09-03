# -*- coding: utf-8 -*-
import json

from datetime import datetime
from pytz import timezone
import requests
import pkg_resources
from django import forms
from sentry.plugins.bases.notify import NotificationPlugin


class MessageForm(forms.Form):
    baseUrl = forms.CharField(help_text=u"域名")
    messageUrl = forms.CharField(help_text=u"消息推送路由")
    tokenUrl = forms.CharField(help_text=u"token获取路由")
    keyUrl = forms.CharField(help_text=u"key获取路由")
    host = forms.CharField(
        help_text=u"Sentry访问的Host(填真实访问的地址，生产一般由Nginx、Apache进行反代，用于发送消息时点击href直接跳转到event页面)，如：http://127.0.0.1:9000",
        required=False,
    )


class MessagePlugin(NotificationPlugin):
    # Generic plugin information
    title = 'message'
    slug = 'message'
    description = u'Sentry报警插件'
    version = pkg_resources.get_distribution("sentry_message_plugin").version
    author = 'zhen.huang'
    author_url = 'https://github.com/a847621843'
    resource_links = [
        ('Source', 'https://github.com/a847621843/sentry-message-plugin'),
    ]

    # Configuration specifics
    conf_key = slug
    conf_title = title

    project_conf_form = MessageForm

    # Should this plugin be enabled by default for projects?
    # project_default_enabled = False

    def is_configured(self, project):
        """
        Check if plugin is configured.
        """
        return bool(self.get_option('messageUrl', project) and
                    self.get_option('baseUrl', project) and
                    self.get_option('tokenUrl', project) and
                    self.get_option('keyUrl', project) and
                    self.get_option('phone', project))

    def notify_users(self, group, event, *args, **kwargs):
        if not self.is_configured(group.project):
            return

        project = event.project
        baseUrl = self.get_option("baseUrl", project)
        messageUrl = self.get_option("messageUrl", project)
        tokenUrl = self.get_option("tokenUrl", project)
        keyUrl = self.get_option("keyUrl", project)
        host = self.get_option("host", project) or ''
        key = requests.get(
            baseUrl+keyUrl,
            verify=False
        ).json().get("key")
        if not key:
            return u'请检查baseUrl、keyUrl是否设置正确'
        access_token = requests.get(
            baseUrl+tokenUrl,
            verify=False,
            params={"key": key}
        ).json().get("access_token")
        if not access_token:
            return u'请检查baseUrl、tokenUrl是否设置正确'

        message = {
            "type":"sentry",
            "sentry":{
                "type":"markdown",
                "projectName":project.slug,
                "level":event.get_tag('level').capitalize(),
                "time":datetime.now(timezone('Asia/Shanghai')).strftime("%Y-%m-%d %H:%M:%S"),
                "message":event.message.encode('utf8'),
                "href":"({}{}events/{}/)".format(host, group.get_absolute_url(), event.id)
            }

        }
        headers = {
            "token":access_token,
        }
        return requests.post(
            baseUrl+messageUrl,
            headers=headers,
            data=json.dumps(message),
            verify=False,
        )

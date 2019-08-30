# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template
from django.conf import settings
from django.template.loader import get_template
from django.utils.text import mark_safe

from coop_bar import get_version
from coop_bar.bar import CoopBar
from coop_bar.utils import context_to_dict

register = template.Library()


class CoopBarNode(template.Node):

    def render(self, context):
        request = context.get("request", None)
        commands = CoopBar().get_commands(request, context)
        if commands:  # hide admin-bar if nothing to display
            css_classes = CoopBar().get_css_classes(request, context)
            context_dict = {'commands': commands, 'css_classes': css_classes}
            the_template = get_template("coop_bar.html")
            return the_template.render(context_dict)
        return ''


@register.tag
def coop_bar(parser, token):
    return CoopBarNode()


class CoopBarHeaderNode(template.Node):

    def __init__(self, option):
        self.option = option

    def render(self, context):
        request = context.get("request", None)

        if request:
            if self.option == "admin-only" and not request.user.is_staff:
                return ''

            if self.option == "auth-only" and not request.user.is_authenticated():
                return ''

        static_url = getattr(settings, 'STATIC_URL', '')
        url = '<link rel="stylesheet" href="{0}css/coop_bar.css?v={1}" type="text/css" />'.format(
            static_url, get_version()
        )
        headers = [mark_safe(url), mark_safe('<link rel="stylesheet" href="{0}fontawesome/css/all.css" type="text/css" />'.format(static_url))]
        headers += CoopBar().get_headers(request, context_to_dict(context))
        return "\n".join(headers)


@register.tag
def coop_bar_headers(parser, token):
    args = token.split_contents()
    option = args[1] if len(args) > 1 else ''
    return CoopBarHeaderNode(option)

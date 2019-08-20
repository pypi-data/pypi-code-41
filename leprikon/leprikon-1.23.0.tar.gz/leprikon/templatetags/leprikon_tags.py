import requests
from django import template
from django.contrib.staticfiles import finders
from django.core.cache import InvalidCacheBackendError, caches
from django.utils.safestring import mark_safe
from lxml.html import fromstring, tostring

from ..conf import settings
from ..forms.schoolyear import SchoolYearForm
from ..utils import (
    comma_separated as _comma_separated, currency as _currency,
    current_url as _current_url, first_upper as _first_upper,
    url_back as _url_back, url_with_back as _url_with_back,
)

register = template.Library()


@register.filter
def currency(value):
    try:
        return _currency(value)
    except (ValueError, TypeError):
        return ''


@register.filter
def comma_separated(value):
    return _comma_separated(value)


@register.filter
def first_upper(value):
    return _first_upper(value)


@register.filter
def filter_current_school_year(value, school_year):
    return value.filter(school_year=school_year)


@register.filter
def lines(value):
    try:
        return value.strip().split('\n')
    except:
        return []


@register.simple_tag
def param_back():
    return settings.LEPRIKON_PARAM_BACK


@register.simple_tag(takes_context=True)
def url_back(context):
    return _url_back(context['request'])


@register.simple_tag(takes_context=True)
def current_url(context):
    return _current_url(context['request'])


@register.inclusion_tag('leprikon/registration_links.html', takes_context=True)
def registration_links(context, subject):
    context = context.__copy__()
    context['subject'] = subject
    if context['request'].user.is_authenticated():
        context['registrations'] = subject.registrations.filter(user=context['request'].user, canceled=None)
    else:
        context['registrations'] = []
    context['registration_url'] = _url_with_back(subject.get_registration_url(), current_url(context))
    return context


@register.inclusion_tag('leprikon/schoolyear_form.html', takes_context=True)
def school_year_form(context):
    context = context.__copy__()
    context['school_year_form'] = SchoolYearForm(context['request'])
    return context


@register.simple_tag
def upstream(url, xpath):
    '''
    If Leprikón is intended to look like another website (the main website of the organization),
    use this tag to include html snippet from the other site to always stay aligned with it.

    Following example includes tag <nav> (with all it's content) from https://example.com:

        {% load cache leprikon_tags %}
        {% cache 300 menu %}{% upstream 'https://example.com/' '//nav' %}{% endcache %}
    '''
    try:
        cache = caches['upstream_pages']
    except InvalidCacheBackendError:
        cache = caches['default']
    try:
        content = cache.get(url)
        if content is None:
            content = requests.get(url).content
            cache.set(url, content, 60)
        return mark_safe(b''.join(
            tostring(node)
            for node in fromstring(content).xpath(xpath)
        ))
    except Exception:
        from traceback import print_exc
        print_exc()
        return ''


class URLWithBackNode(template.base.Node):
    def __init__(self, original_node):
        self.original_node = original_node

    def render(self, context):
        return _url_with_back(
            self.original_node.render(context),
            current_url(context),
        )


@register.tag
def url_with_back(parser, token):
    """
    Returns an absolute URL as built-in tag url does,
    but adds parameter back with current url.
    """
    return URLWithBackNode(template.defaulttags.url(parser, token))


@register.simple_tag(takes_context = True)
def query_string(context, key, value):
    get = context['request'].GET.copy()
    get[key] = value
    return get.urlencode()


@register.simple_tag
def font(name):
    return finders.find(name)

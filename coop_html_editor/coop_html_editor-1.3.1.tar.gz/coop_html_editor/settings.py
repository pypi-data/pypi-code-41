# -*- coding: utf-8 -*-
"""centralize settings"""

from django.conf import settings as project_settings
from django.core.exceptions import ImproperlyConfigured
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def get_field_prefix():
    """return the prefix to use in form field names"""
    return "html_editor"


def get_html_editor():
    """return the name of the editor to use: aloha or ck-editor"""
    editor_name = getattr(project_settings, 'COOP_HTML_EDITOR', "aloha")
    supported_editors = ('aloha', 'ck-editor')
    if editor_name not in supported_editors:
        raise ImproperlyConfigured(
            u'Unknown editor {0}. Allowed choices: {1}'.format(editor_name, supported_editors)
        )
    return editor_name


def aloha_version():
    """return settings or default"""
    return getattr(project_settings, 'ALOHA_VERSION', "aloha.0.23.26")


def ckeditor_version():
    """return settings or default"""
    return getattr(project_settings, 'CKEDITOR_VERSION', "ckeditor.4.6.2")


def init_js_template():
    """return settings or default"""
    if get_html_editor() == 'ck-editor':
        return getattr(project_settings, 'CKEDITOR_INIT_JS_TEMPLATE', "html_editor/ckeditor-init.js")
    else:
        return getattr(project_settings, 'ALOHA_INIT_JS_TEMPLATE', "html_editor/aloha_init.js")


def init_url():
    """return settings or default"""
    url = getattr(project_settings, 'COOP_HTML_EDITOR_INIT_URL', None)
    if not url:
        url = getattr(project_settings, 'ALOHA_INIT_URL', None)
    return url or reverse('html_editor_init')


def plugins():
    """return settings or default"""
    plugins_ = getattr(project_settings, 'ALOHA_PLUGINS', None)
    if not plugins_:
        plugins_ = (
            "common/format",
            #"custom/format",
            "common/highlighteditables",
            "common/list",
            "common/link",
            "common/undo",
            "common/paste",
            "common/commands",
            "common/contenthandler",
            "common/image",
            #"custom/zimage",
            "common/align",
            #"extra/attributes",
            "common/characterpicker",
            #"common/abbr",
            "common/horizontalruler",
            #"common/table",
            #"extra/metaview",
            #"extra/textcolor",
        )
    return plugins_


def skip_jquery():
    """return settings or default"""
    return getattr(project_settings, 'ALOHA_SKIP_JQUERY', False)
    

def jquery_version():
    """return settings or default"""
    if project_settings.DEBUG:
        return getattr(project_settings, 'ALOHA_JQUERY', "js/jquery-1.7.2.js")
    else:
        return getattr(project_settings, 'ALOHA_JQUERY', "js/jquery-1.7.2.js")
    

def jquery_no_conflict():
    """return settings or default"""
    return getattr(project_settings, 'ALOHA_JQUERY_NO_CONFLICT', True)
    

def link_models():
    """return settings or default"""
    return getattr(project_settings, 'HTML_EDITOR_LINK_MODELS', ())


def image_models():
    """return settings or default"""
    return getattr(project_settings, 'HTML_EDITOR_IMAGE_MODELS', ())


def sidebar_disabled():
    """return settings or default"""
    return getattr(project_settings, 'ALOHA_SIDEBAR_DISABLED', True)
    

def css_classes():
    """return settings or default"""
    if get_html_editor() == 'ck-editor':
        # Example
        # CKEDITOR_CSS_CLASSES = [
        #     "{name: 'Highlight', element: 'span', attributes: {'class': 'highlight'}}",
        #     "{name: 'Red Title', element: 'h3', styles: {color: '#880000'}}",
        # ]
        return getattr(project_settings, 'CKEDITOR_CSS_CLASSES', [])
    else:
        return getattr(project_settings, 'ALOHA_CSS_CLASSES', ())


def image_default_class():
    if get_html_editor() == 'ck-editor':
        return getattr(project_settings, 'CKEDITOR_IMAGE_DEFAULT_CLASS', '')


def resize_disabled():
    """return settings or default"""
    return getattr(project_settings, 'ALOHA_RESIZE_DISABLED', False)

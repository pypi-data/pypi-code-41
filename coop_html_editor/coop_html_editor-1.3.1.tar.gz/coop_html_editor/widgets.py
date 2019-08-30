# -*- coding: utf-8 -*-
"""widgets to be used in a form"""

from bs4 import BeautifulSoup
import logging

from django.forms import Media

import floppyforms.__future__ as floppyforms

from . import settings


def get_inline_html_widget():
    """returns the Input field to use"""
    editor_name = settings.get_html_editor()
    input_class = {
        'aloha': AlohaInput,
        'ck-editor': CkEditorInput,
    }[editor_name]
    return input_class()


class BaseInlineHtmlInput(floppyforms.widgets.TextInput):
    """Base class for Inline HtmlInput"""
    clean_value_callbacks = []

    def get_context(self, *args, **kwargs):
        """get context"""
        context = super(BaseInlineHtmlInput, self).get_context(*args, **kwargs)
        context.update({'field_prefix': settings.get_field_prefix()})
        return context

    def value_from_datadict(self, data, files, name):
        """return value"""
        value = super(BaseInlineHtmlInput, self).value_from_datadict(data, files, name)
        return self.clean_value(value)

    def clean_value(self, origin_value):
        """This apply several fixes on the html"""
        return_value = origin_value
        if return_value:  # don't manage None values
            for callback in self.clean_value_callbacks:
                return_value = callback(return_value)
        return return_value


class CkEditorInput(BaseInlineHtmlInput):
    """
    Text widget with CK-Editor html editor
    requires floppyforms to be installed
    """

    template_name = 'html_editor/ckeditor_input.html'

    @property
    def media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        """
        init_url = settings.init_url()

        try:
            css = {
                'all': (

                )
            }

            js_files = [
                '{0}/ckeditor.js'.format(settings.ckeditor_version()),
                init_url,
            ]

            return Media(css=css, js=js_files)

        except Exception as msg:
            django_logger = logging.getLogger('django')
            django_logger.error(u'CkEditorInput._get_media Error {0}'.format(msg))


class AlohaInput(BaseInlineHtmlInput):
    """
    Text widget with aloha html editor
    requires floppyforms to be installed
    """
    template_name = 'html_editor/aloha_input.html'

    def __init__(self, *args, **kwargs):
        # for compatibility with previous versions
        self.aloha_plugins = kwargs.pop('aloha_plugins', None)
        self.extra_aloha_plugins = kwargs.pop('extra_aloha_plugins', None)
        self.aloha_init_url = kwargs.pop('aloha_init_url', None)
        super(AlohaInput, self).__init__(*args, **kwargs)
        self.clean_value_callbacks = (self._fix_br, self._fix_img,)

    def _fix_br(self, content):
        """
        This change the <br> tag into <br />
        in order to avoid empty lines at the end in  HTML4 for example for newsletters
        """
        return content.replace('<br>', '<br />')

    def _fix_img(self, content):
        """Remove the handlers generated on the image for resizing. It may be not removed by editor in some cases"""
        soup = BeautifulSoup(content, 'html.parser')

        wrapped_img = soup.select(".ui-wrapper img")
        if len(wrapped_img) > 0:
            img = wrapped_img[0]

            # Remove the ui-resizable class
            img_classes = img.get('class', None) or []
            img_classes.remove('ui-resizable')
            img['class'] = img_classes

            # Replace the ui-wrapper by the img
            wrapper = soup.select(".ui-wrapper")[0]
            wrapper.replace_with(img)

            content = u'{0}'.format(soup)

        return content

    @property
    def media(self):
        """
        return code for inserting required js and css files
        need aloha , plugins and initialization
        """
        try:
            aloha_init_url = self.aloha_init_url or settings.init_url()
            aloha_version = settings.aloha_version()

            aloha_plugins = self.aloha_plugins
            if not aloha_plugins:
                aloha_plugins = settings.plugins()

            if self.extra_aloha_plugins:
                aloha_plugins = tuple(aloha_plugins) + tuple(self.extra_aloha_plugins)

            css = {
                'all': (
                    "{0}/css/aloha.css".format(aloha_version),
                )
            }

            js_files = []

            if not settings.skip_jquery():
                js_files.append(settings.jquery_version())

            # if aloha_version.startswith('aloha.0.22.') or aloha_version.startswith('aloha.0.23.'):
            js_files.append("{0}/lib/require.js".format(aloha_version))

            js_files.append(aloha_init_url)
            js_files.append(
                u'{0}/lib/aloha.js" data-aloha-plugins="{1}'.format(aloha_version, u",".join(aloha_plugins))
            )
            js_files.append('html-editor/js/aloha-init.js')
            
            return Media(css=css, js=js_files)
        except Exception as msg:
            django_logger = logging.getLogger('django')
            django_logger.error(u'AlohaInput._get_media Error {0}'.format(msg))

from django import forms
from django.forms import widgets
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.conf import settings

from .utils import json_dumps


class RedactorEditor(widgets.Textarea):
    def __init__(self, *args, **kwargs):
        upload_to = kwargs.pop('upload_to', None)
        self.options = dict(getattr(settings, 'REDACTOR_OPTIONS', {}))
        self.options.update(kwargs.pop('redactor_options', {}))

        if kwargs.pop('allow_file_upload', True):
            self.options['fileUpload'] = reverse_lazy(
                'redactor_upload_file', kwargs={'upload_to': upload_to}
            )
        if kwargs.pop('allow_image_upload', True):
            self.options['imageUpload'] = reverse_lazy(
                'redactor_upload_image', kwargs={'upload_to': upload_to}
            )

        super(RedactorEditor, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, renderer=None, **kwargs):
        """
        Must parse self.options with json_dumps on self.render.
        Because at some point Django calls RedactorEditor.__init__ before
        loading the urls, and it will break.
        """
        attrs['data-options'] = json_dumps(self.options)
        attrs['data-type'] = 'imperavi-editor'
        html = super(RedactorEditor, self).render(name, value, attrs, renderer, **kwargs)

        return mark_safe(html)

    def _media(self):
        js = (
            'redactor/redactor.min.js',
            'redactor/langs/{}.js'.format(self.options.get('lang', 'ru')),
        )

        for plugin in self.options.get('plugins', []):
            js = js + (
                'redactor/plugins/{}/{}.js'.format(plugin, plugin),
            )

        js = js + (
            'redactor/init.js',
        )

        css = {
            'all': (
                'redactor/redactor.min.css',
                'redactor/override-redactor.css',
            )
        }

        return forms.Media(css=css, js=js)
    media = property(_media)

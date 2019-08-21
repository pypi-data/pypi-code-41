from django.apps import AppConfig
from django.utils.translation import lazy_gettext as _


class WagtailpersonConfig(AppConfig):
    name = 'wagtailperson'
    verbose_name = _('Wagtail Person')

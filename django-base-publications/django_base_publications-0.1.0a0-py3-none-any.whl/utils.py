from urllib.parse import urlunsplit
from enum import Enum, EnumMeta
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.sites.models import Site


class NamedEnumMeta(EnumMeta):
    def __iter__(cls):
        return (
            (cls._member_map_[name].value, _(cls._member_map_[name]))
            for name in cls._member_names_
        )


class NamedEnum(Enum, metaclass=NamedEnumMeta):
    pass


def get_item_absolute_site_url(item_url: str, query: str = '', fragment: str = ''):
    site = Site.objects.get_current()
    return urlunsplit((settings.SITE_SCHEME, site.domain, item_url, query, fragment))

from enum import Enum, EnumMeta
from django.utils.translation import gettext_lazy as _


class NamedEnumMeta(EnumMeta):
    def __iter__(cls):
        return (
            (cls._member_map_[name].value, _(cls._member_map_[name].value))
            for name in cls._member_names_
        )


class NamedEnum(Enum, metaclass=NamedEnumMeta):
    pass

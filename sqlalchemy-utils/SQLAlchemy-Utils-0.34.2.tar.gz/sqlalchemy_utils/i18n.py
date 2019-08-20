import inspect

import six
import sqlalchemy as sa
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql.expression import ColumnElement

from .exceptions import ImproperlyConfigured

try:
    import babel
    import babel.dates
except ImportError:
    babel = None


def get_locale():
    try:
        return babel.Locale('en')
    except AttributeError:
        # As babel is optional, we may raise an AttributeError accessing it
        raise ImproperlyConfigured(
            'Could not load get_locale function using Babel. Either '
            'install Babel or make a similar function and override it '
            'in this module.'
        )


if six.PY2:
    def get_args_count(func):
        if (
            callable(func) and
            not inspect.isfunction(func) and
            not inspect.ismethod(func)
        ):
            func = func.__call__
        args = inspect.getargspec(func).args
        return len(args) - 1 if inspect.ismethod(func) else len(args)
else:
    def get_args_count(func):
        return len(inspect.signature(func).parameters)


def cast_locale(obj, locale, attr):
    """
    Cast given locale to string. Supports also callbacks that return locales.

    :param obj:
        Object or class to use as a possible parameter to locale callable
    :param locale:
        Locale object or string or callable that returns a locale.
    """
    if callable(locale):
        args_count = get_args_count(locale)
        if args_count == 0:
            locale = locale()
        elif args_count == 1:
            locale = locale(obj)
        elif args_count == 2:
            locale = locale(obj, attr.key)
    if isinstance(locale, babel.Locale):
        return str(locale)
    return locale


class cast_locale_expr(ColumnElement):
    def __init__(self, cls, locale, attr):
        self.cls = cls
        self.locale = locale
        self.attr = attr


@compiles(cast_locale_expr)
def compile_cast_locale_expr(element, compiler, **kw):
    locale = cast_locale(element.cls, element.locale, element.attr)
    if isinstance(locale, six.string_types):
        return "'{0}'".format(locale)
    return compiler.process(locale)


class TranslationHybrid(object):
    def __init__(self, current_locale, default_locale, default_value=None):
        if babel is None:
            raise ImproperlyConfigured(
                'You need to install babel in order to use TranslationHybrid.'
            )
        self.current_locale = current_locale
        self.default_locale = default_locale
        self.default_value = default_value

    def getter_factory(self, attr):
        """
        Return a hybrid_property getter function for given attribute. The
        returned getter first checks if object has translation for current
        locale. If not it tries to get translation for default locale. If there
        is no translation found for default locale it returns None.
        """
        def getter(obj):
            current_locale = cast_locale(obj, self.current_locale, attr)
            try:
                return getattr(obj, attr.key)[current_locale]
            except (TypeError, KeyError):
                default_locale = cast_locale(obj, self.default_locale, attr)
                try:
                    return getattr(obj, attr.key)[default_locale]
                except (TypeError, KeyError):
                    return self.default_value
        return getter

    def setter_factory(self, attr):
        def setter(obj, value):
            if getattr(obj, attr.key) is None:
                setattr(obj, attr.key, {})
            locale = cast_locale(obj, self.current_locale, attr)
            getattr(obj, attr.key)[locale] = value
        return setter

    def expr_factory(self, attr):
        def expr(cls):
            cls_attr = getattr(cls, attr.key)
            current_locale = cast_locale_expr(cls, self.current_locale, attr)
            default_locale = cast_locale_expr(cls, self.default_locale, attr)
            return sa.func.coalesce(
                cls_attr[current_locale],
                cls_attr[default_locale]
            )
        return expr

    def __call__(self, attr):
        return hybrid_property(
            fget=self.getter_factory(attr),
            fset=self.setter_factory(attr),
            expr=self.expr_factory(attr)
        )

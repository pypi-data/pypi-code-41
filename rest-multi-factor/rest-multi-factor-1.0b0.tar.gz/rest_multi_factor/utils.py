"""Utilities for multi-factor authentication."""

__all__ = (
    "unify_queryset",
    "get_user_model",
    "get_token_model",
    "get_subclassed_models",
)

from django import VERSION
from django.apps import apps
from django.contrib.auth import get_user_model
from django.db.models.query import EmptyQuerySet, Q
from django.core.exceptions import ImproperlyConfigured


from rest_multi_factor.settings import multi_factor_settings


def get_token_model():
    """
    Helper function to retrieve the token model that should be used.

    This method has the same signature as
    `django.contrib.auth.get_user_model`.

    :raises ImproperlyConfigured: If the format of the 'AUTH_TOKEN_MODEL'
    setting is incorrect or if it could not been found.
    """
    try:
        return apps.get_model(
            multi_factor_settings.AUTH_TOKEN_MODEL, require_ready=False
        )

    except ValueError:
        raise ImproperlyConfigured(
            "AUTH_TOKEN_MODEL must be of the form 'app_label.model_name'"
        )

    except LookupError:
        raise ImproperlyConfigured(
            "AUTH_TOKEN_MODEL refers to model '{AUTH_TOKEN_MODEL}' "
            "that has not been installed".format(
                AUTH_TOKEN_MODEL=multi_factor_settings.AUTH_TOKEN_MODEL
            )
        )


def get_subclassed_models(base):
    """
    Get all models that are subclassed from a base model.

    This can be useful for models that inherit from a
    abstract base model that defines fields that need to
    be compared at all together.

    :param base: The base model
    :type base: type of django.db.models.base.Model

    :return: All subclasses models
    :rtype: tuple
    """
    models = apps.get_models()

    return tuple(m for m in models if issubclass(m, base))


def get_model_fields(model):
    """
    Retrieve the field names of a model.

    :param model: The model to extract the field names from

    :return: The names of the fields of a model
    :rtype: tuple of str
    """
    meta = getattr(model, "_meta")
    return tuple(field.name for field in meta.get_fields())


def unify_queryset(base, fields=None, filter=None, queryset=None):
    """
    Unify sub models of another model.

    This function combines the process of filtering
    selecting and unifying field by using SQL's UNION operator
    and filtering before joining.

    :param base: The base class to use
    :type base: type of django.db.models.base.Model

    :param fields: The fields to select within the query
    :type fields: tuple of str

    :param filter: The filter to use for every queryset before UNION
    :type filter: django.db.models.query.Q

    :param queryset: The base queryset to use
    :type queryset:

    :return: A new queryset that unified all subclassed models of base
    :rtype: django.db.models.
    """
    filter = filter or Q()
    fields = fields or get_model_fields(base)
    models = get_subclassed_models(base)

    queryset = queryset or models[0].objects.none()
    filtered = (m.objects.order_by() for m in models)
    filtered = (q.filter(filter).values(*fields) for q in filtered)

    # ticket: https://code.djangoproject.com/ticket/28293
    if VERSION < (2, 0, 0) and isinstance(queryset, EmptyQuerySet):
        filtered = list(filtered)  # pragma: no cover
        queryset = filtered.pop(0)  # pragma: no cover

    return queryset.union(*filtered, all=True)

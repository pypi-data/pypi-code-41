# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.db.models.query import QuerySet
from django.db.models.sql import EmptyResultSet

from .mixins import (
    CacheBackendMixin,
    CacheInvalidateMixin,
    CacheKeyMixin,
)

logger = logging.getLogger(__name__)


class CacheManager(CacheInvalidateMixin, models.Manager):
    """
    Custom model manager that returns CachingQuerySet
    """

    # Use this manager when accessing objects that are related to from some other model.
    # Works only for one-to-one relationships not for many-to-many or foreign keys. See https://code.djangoproject.com/ticket/14891
    # so post_save, post_delete signals are used for cache invalidation. Signals can be removed when this bug is fixed.
    # https://docs.djangoproject.com/en/2.2/topics/db/managers/#base-managers
    # django <=2
    use_for_related_fields = True
    # django >=2
    # custom_manager = CustomManager()
    # class Meta:
    #     base_manager_name = 'custom_manager'

    # django <=1.5
    def get_query_set(self):
        return CachingQuerySet(self.model, using=self._db)

    def get_queryset(self):
        return CachingQuerySet(self.model, using=self._db)


class CachingQuerySet(CacheBackendMixin, CacheKeyMixin, CacheInvalidateMixin, QuerySet):
    """
    Custom query set that caches results on load. This query set will force iteration of the result set
    so that the results can be cached for future calls.

    Query set invalidates model cache for any calls to bulk_create or update.
    """

    def iterator(self):
        try:
            key = self.generate_key()
        # workaround for Django bug # 12717
        except EmptyResultSet:
            return
        result_set = self.cache_backend.get(key)
        if result_set is None:
            logger.debug('CACHE MISS {0}'.format(key))
            result_set = list(super(CachingQuerySet, self).iterator())
            self.cache_backend.set(key, result_set)
        for result in result_set:
            yield result

    def _fetch_all(self):
        if self._result_cache is None:
            try:
                key = self.generate_key()
            # workaround for Django bug # 12717
            except EmptyResultSet:
                self._result_cache = []
                return
            self._result_cache = self.cache_backend.get(key)

            if self._result_cache is None:
                logger.debug('CACHE MISS {0}'.format(key))
                self._result_cache = list(self._iterable_class(self))
                self.cache_backend.set(key, self._result_cache)
            else:
                logger.debug('CACHE HIT {0}'.format(key))
        super(CachingQuerySet, self)._fetch_all()

    def bulk_create(self, *args, **kwargs):
        self.invalidate_model_cache()
        return super(CachingQuerySet, self).bulk_create(*args, **kwargs)

    def update(self, **kwargs):
        self.invalidate_model_cache()
        return super(CachingQuerySet, self).update(**kwargs)

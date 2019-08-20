# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django
from django.db import models
from django.utils.timezone import now


# DELIBERATELY STOLEN FROM https://github.com/carljm/django-model-utils/blob/master/model_utils/fields.py


class MonitorField(models.DateTimeField):
    """
    A DateTimeField that monitors another field on the same model and
    sets itself to the current date/time whenever the monitored field
    changes.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', now)
        monitor = kwargs.pop('monitor', None)
        if not monitor:
            raise TypeError(
                '%s requires a "monitor" argument' % self.__class__.__name__)
        self.monitor = monitor
        when = kwargs.pop('when', None)
        if when is not None:
            when = set(when)
        self.when = when
        super(MonitorField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name):
        self.monitor_attname = '_monitor_%s' % name
        models.signals.post_init.connect(self._save_initial, sender=cls)
        super(MonitorField, self).contribute_to_class(cls, name)

    def get_monitored_value(self, instance):
        return getattr(instance, self.monitor)

    def _save_initial(self, sender, instance, **kwargs):
        if django.VERSION >= (1, 10) and self.monitor in instance.get_deferred_fields():
            # Fix related to issue #241 to avoid recursive error on double monitor fields
            return
        setattr(instance, self.monitor_attname,
                self.get_monitored_value(instance))

    def pre_save(self, model_instance, add):
        value = now()
        previous = getattr(model_instance, self.monitor_attname, None)
        current = self.get_monitored_value(model_instance)
        if previous != current:
            if self.when is None or current in self.when:
                setattr(model_instance, self.attname, value)
                self._save_initial(model_instance.__class__, model_instance)
        return super(MonitorField, self).pre_save(model_instance, add)

    def deconstruct(self):
        name, path, args, kwargs = super(MonitorField, self).deconstruct()
        kwargs['monitor'] = self.monitor
        if self.when is not None:
            kwargs['when'] = self.when
        return name, path, args, kwargs

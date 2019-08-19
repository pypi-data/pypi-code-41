from revops.resources import APIResource
from revops.schema import EventMetricSchema, UsageEventSchema
from revops.exceptions import RequestSchemaException

from marshmallow import Schema, fields
from datetime import datetime, timezone


class EventMetric(APIResource):
    account_id = None
    metadata = {}
    metric_name = None
    metric_value = 0
    product = None
    time_period = None

    def create(self, **kwargs):
        self._copy_properties(**kwargs)
        event_metric_schema = EventMetricSchema()
        event_metric_schema.load(kwargs)
        return self

class UsageEvent(APIResource):
    _resource = "v1/usage/events"
    _metrics = []
    _marshaler = UsageEventSchema

    id = None
    date_submitted = None
    event_metrics = []
    mode = None
    usage_event_id = None
    transaction_id = None

    def add_metric(self, **kwargs):
        metric = EventMetric(self._api)
        metric.create(**kwargs)
        self.event_metrics.append(metric)

    def create(self, **kwargs):
        self.event_metrics = []
        self.date_submitted = kwargs.get(
            'date_submitted', self.get_current_time()
        )

        response, errors = self._marshaler().load(data=kwargs)
        if len(errors) > 0:
            raise RequestSchemaException(
                message="Unable to create UsageEvent",
                errors=errors,
                resource=self._resource,
            )
        self._copy_properties(**kwargs)
        return self

    def commit(self):
        return self.request(http_method = "POST")

    def delete(self, id = None):
        if id is not None:
            self.id = id

        if self.id == None and id == None:
            raise RequestSchemaException(
                message="Unable to delete UsageEvent, id is not set.",
                errors=[],
                resource=self._resource,
            )
        return self.request(http_method = "DELETE", sub_resource="/{}".format(self.id))

"""
Defines the records module
revops.usage.records.<action>
"""
class __api_module__(object):

    def __init__(self, api):
        self._api = api

    @property
    def events(self):
        return UsageEvent(self._api)

# *** WARNING: this file was generated by the Pulumi Kubernetes codegen tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
from typing import Optional

import pulumi
import pulumi.runtime
from pulumi import Input, ResourceOptions

from ... import tables, version


class Event(pulumi.CustomResource):
    """
    Event is a report of an event somewhere in the cluster.
    """

    def __init__(self, resource_name, opts=None, action=None, count=None, event_time=None, first_timestamp=None, involved_object=None, last_timestamp=None, message=None, metadata=None, reason=None, related=None, reporting_component=None, reporting_instance=None, series=None, source=None, type=None, __name__=None, __opts__=None):
        """
        Create a Event resource with the given unique name, arguments, and options.
        """
        if __name__ is not None:
            warnings.warn("explicit use of __name__ is deprecated", DeprecationWarning)
            resource_name = __name__
        if __opts__ is not None:
            warnings.warn("explicit use of __opts__ is deprecated, use 'opts' instead", DeprecationWarning)
            opts = __opts__
        if not resource_name:
            raise TypeError('Missing resource name argument (for URN creation)')
        if not isinstance(resource_name, str):
            raise TypeError('Expected resource name to be a string')
        if opts and not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')

        __props__ = dict()

        __props__['apiVersion'] = 'v1'
        __props__['kind'] = 'Event'
        if involved_object is None:
            raise TypeError('Missing required property involved_object')
        __props__['involvedObject'] = involved_object
        if metadata is None:
            raise TypeError('Missing required property metadata')
        __props__['metadata'] = metadata
        __props__['action'] = action
        __props__['count'] = count
        __props__['eventTime'] = event_time
        __props__['firstTimestamp'] = first_timestamp
        __props__['lastTimestamp'] = last_timestamp
        __props__['message'] = message
        __props__['reason'] = reason
        __props__['related'] = related
        __props__['reportingComponent'] = reporting_component
        __props__['reportingInstance'] = reporting_instance
        __props__['series'] = series
        __props__['source'] = source
        __props__['type'] = type

        if opts is None:
            opts = pulumi.ResourceOptions()
        if opts.version is None:
            opts.version = version.get_version()

        super(Event, self).__init__(
            "kubernetes:core/v1:Event",
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(name: str, id: Input[str], opts: Optional[ResourceOptions] = None):
        opts = ResourceOptions(id=id) if opts is None else opts.merge(ResourceOptions(id=id))
        return Event(name, opts)

    def translate_output_property(self, prop: str) -> str:
        return tables._CASING_FORWARD_TABLE.get(prop) or prop

    def translate_input_property(self, prop: str) -> str:
        return tables._CASING_BACKWARD_TABLE.get(prop) or prop

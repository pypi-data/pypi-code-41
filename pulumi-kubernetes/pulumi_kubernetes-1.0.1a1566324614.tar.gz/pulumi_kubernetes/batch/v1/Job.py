# *** WARNING: this file was generated by the Pulumi Kubernetes codegen tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
from typing import Optional

import pulumi
import pulumi.runtime
from pulumi import Input, ResourceOptions

from ... import tables, version


class Job(pulumi.CustomResource):
    """
    Job represents the configuration of a single job.
    
    This resource currently does not wait until it is ready before registering
    success for create/update and populating output properties from the current
    state of the resource. Work to add readiness checks is in progress [1].
    
    [1] https://github.com/pulumi/pulumi-kubernetes/pull/633
    
    """

    def __init__(self, resource_name, opts=None, metadata=None, spec=None, status=None, __name__=None, __opts__=None):
        """
        Create a Job resource with the given unique name, arguments, and options.
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

        __props__['apiVersion'] = 'batch/v1'
        __props__['kind'] = 'Job'
        __props__['metadata'] = metadata
        __props__['spec'] = spec
        __props__['status'] = status

        if opts is None:
            opts = pulumi.ResourceOptions()
        if opts.version is None:
            opts.version = version.get_version()

        super(Job, self).__init__(
            "kubernetes:batch/v1:Job",
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(name: str, id: Input[str], opts: Optional[ResourceOptions] = None):
        opts = ResourceOptions(id=id) if opts is None else opts.merge(ResourceOptions(id=id))
        return Job(name, opts)

    def translate_output_property(self, prop: str) -> str:
        return tables._CASING_FORWARD_TABLE.get(prop) or prop

    def translate_input_property(self, prop: str) -> str:
        return tables._CASING_BACKWARD_TABLE.get(prop) or prop

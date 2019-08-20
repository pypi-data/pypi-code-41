# *** WARNING: this file was generated by the Pulumi Kubernetes codegen tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import warnings
from typing import Optional

import pulumi
import pulumi.runtime
from pulumi import Input, ResourceOptions

from ... import tables, version


class Ingress(pulumi.CustomResource):
    """
    Ingress is a collection of rules that allow inbound connections to reach the endpoints defined
    by a backend. An Ingress can be configured to give services externally-reachable urls, load
    balance traffic, terminate SSL, offer name based virtual hosting etc. DEPRECATED - This group
    version of Ingress is deprecated by networking.k8s.io/v1beta1 Ingress. See the release notes for
    more information.
    
    This resource waits until it is ready before registering success for
    create/update and populating output properties from the current state of the resource.
    The following conditions are used to determine whether the resource creation has
    succeeded or failed:
    1.  Ingress object exists.
    2.  Endpoint objects exist with matching names for each Ingress path (except when Service
        type is ExternalName).
    3.  Ingress entry exists for '.status.loadBalancer.ingress'.
    
    If the Ingress has not reached a Ready state after 10 minutes, it will
    time out and mark the resource update as Failed. You can override the default timeout value
    by setting 'pulumi.com/timeoutSeconds' as a '.metadata.annotation' on the resource.
    This approach will be deprecated in favor of customTimeouts. See
    https://github.com/pulumi/pulumi-kubernetes/issues/672 for details.
    """

    def __init__(self, resource_name, opts=None, metadata=None, spec=None, status=None, __name__=None, __opts__=None):
        """
        Create a Ingress resource with the given unique name, arguments, and options.
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

        __props__['apiVersion'] = 'extensions/v1beta1'
        __props__['kind'] = 'Ingress'
        __props__['metadata'] = metadata
        __props__['spec'] = spec
        __props__['status'] = status

        if opts is None:
            opts = pulumi.ResourceOptions()
        if opts.version is None:
            opts.version = version.get_version()

        super(Ingress, self).__init__(
            "kubernetes:extensions/v1beta1:Ingress",
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(name: str, id: Input[str], opts: Optional[ResourceOptions] = None):
        opts = ResourceOptions(id=id) if opts is None else opts.merge(ResourceOptions(id=id))
        return Ingress(name, opts)

    def translate_output_property(self, prop: str) -> str:
        return tables._CASING_FORWARD_TABLE.get(prop) or prop

    def translate_input_property(self, prop: str) -> str:
        return tables._CASING_BACKWARD_TABLE.get(prop) or prop

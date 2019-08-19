# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator 2.3.33.0
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from .service_create_request import ServiceCreateRequest


class AKSServiceCreateRequest(ServiceCreateRequest):
    """Request to create an AKS service.

    :param name: The service name.
    :type name: str
    :param description: The description of the service.
    :type description: str
    :param tags: Service tag list
    :type tags: list[str]
    :param kv_tags: Service tag dictionary
    :type kv_tags: dict[str, str]
    :param properties: Service property dictionary
    :type properties: dict[str, str]
    :param compute_type: The compute environment type for the service.
     Possible values include: 'ACI', 'BATCH', 'AKS', 'FPGA'
    :type compute_type: str or ~_restclient.models.enum
    :param service_create_request_type_discriminator: Constant filled by
     server.
    :type service_create_request_type_discriminator: str
    :param image_id: The id of the image.
    :type image_id: str
    :param num_replicas: Number of replicas on the cluster.
    :type num_replicas: int
    :param data_collection:
    :type data_collection: ~_restclient.models.ModelDataCollection
    :param compute_name: Id of the compute resource.
    :type compute_name: str
    :param app_insights_enabled: Enable or disable app insights.
    :type app_insights_enabled: bool
    :param auto_scaler:
    :type auto_scaler: ~_restclient.models.AutoScaler
    :param container_resource_requirements:
    :type container_resource_requirements:
     ~_restclient.models.ContainerResourceRequirements
    :param liveness_probe_requirements:
    :type liveness_probe_requirements:
     ~_restclient.models.LivenessProbeRequirements
    :param max_concurrent_requests_per_container: Maximum number of concurrent
     requests per container.
    :type max_concurrent_requests_per_container: int
    :param max_queue_wait_ms: Maximum time a message will wait in the queue
     (in milliseconds).
    :type max_queue_wait_ms: int
    :param keys:
    :type keys: ~_restclient.models.AuthKeys
    :param scoring_timeout_ms: Scoring timeout in milliseconds.
    :type scoring_timeout_ms: int
    """

    _validation = {
        'name': {'required': True},
        'compute_type': {'required': True},
        'service_create_request_type_discriminator': {'required': True},
        'image_id': {'required': True},
        'compute_name': {'required': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'tags': {'key': 'tags', 'type': '[str]'},
        'kv_tags': {'key': 'kvTags', 'type': '{str}'},
        'properties': {'key': 'properties', 'type': '{str}'},
        'compute_type': {'key': 'computeType', 'type': 'str'},
        'service_create_request_type_discriminator': {'key': 'serviceCreateRequestTypeDiscriminator', 'type': 'str'},
        'image_id': {'key': 'imageId', 'type': 'str'},
        'num_replicas': {'key': 'numReplicas', 'type': 'int'},
        'data_collection': {'key': 'dataCollection', 'type': 'ModelDataCollection'},
        'compute_name': {'key': 'computeName', 'type': 'str'},
        'app_insights_enabled': {'key': 'appInsightsEnabled', 'type': 'bool'},
        'auto_scaler': {'key': 'autoScaler', 'type': 'AutoScaler'},
        'container_resource_requirements': {'key': 'containerResourceRequirements', 'type': 'ContainerResourceRequirements'},
        'liveness_probe_requirements': {'key': 'livenessProbeRequirements', 'type': 'LivenessProbeRequirements'},
        'max_concurrent_requests_per_container': {'key': 'maxConcurrentRequestsPerContainer', 'type': 'int'},
        'max_queue_wait_ms': {'key': 'maxQueueWaitMs', 'type': 'int'},
        'keys': {'key': 'keys', 'type': 'AuthKeys'},
        'scoring_timeout_ms': {'key': 'scoringTimeoutMs', 'type': 'int'},
    }

    def __init__(self, name, compute_type, image_id, compute_name, description=None, tags=None, kv_tags=None, properties=None, num_replicas=None, data_collection=None, app_insights_enabled=None, auto_scaler=None, container_resource_requirements=None, liveness_probe_requirements=None, max_concurrent_requests_per_container=None, max_queue_wait_ms=None, keys=None, scoring_timeout_ms=None):
        super(AKSServiceCreateRequest, self).__init__(name=name, description=description, tags=tags, kv_tags=kv_tags, properties=properties, compute_type=compute_type)
        self.image_id = image_id
        self.num_replicas = num_replicas
        self.data_collection = data_collection
        self.compute_name = compute_name
        self.app_insights_enabled = app_insights_enabled
        self.auto_scaler = auto_scaler
        self.container_resource_requirements = container_resource_requirements
        self.liveness_probe_requirements = liveness_probe_requirements
        self.max_concurrent_requests_per_container = max_concurrent_requests_per_container
        self.max_queue_wait_ms = max_queue_wait_ms
        self.keys = keys
        self.scoring_timeout_ms = scoring_timeout_ms
        self.service_create_request_type_discriminator = 'AKSServiceCreateRequest'

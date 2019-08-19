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

from msrest.serialization import Model


class TelemetryMetricsDto(Model):
    """TelemetryMetricsDto.

    :param run_id:
    :type run_id: str
    :param service_name:
    :type service_name: str
    :param type: Possible values include: 'MMS'
    :type type: str or ~_restclient.models.enum
    :param metrics:
    :type metrics: dict[str, str]
    """

    _attribute_map = {
        'run_id': {'key': 'runId', 'type': 'str'},
        'service_name': {'key': 'serviceName', 'type': 'str'},
        'type': {'key': 'type', 'type': 'str'},
        'metrics': {'key': 'metrics', 'type': '{str}'},
    }

    def __init__(self, run_id=None, service_name=None, type=None, metrics=None):
        super(TelemetryMetricsDto, self).__init__()
        self.run_id = run_id
        self.service_name = service_name
        self.type = type
        self.metrics = metrics

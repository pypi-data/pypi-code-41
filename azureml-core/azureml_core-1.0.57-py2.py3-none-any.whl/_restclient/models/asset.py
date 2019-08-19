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


class Asset(Model):
    """Asset.

    :param id: The asset id.
    :type id: str
    :param name: The asset name.
    :type name: str
    :param description: The asset description.
    :type description: str
    :param artifacts: List of artifacts.
    :type artifacts: list[~_restclient.models.Artifact]
    :param tags: The list of asset tags.
    :type tags: list[str]
    :param runid: Run id of the asset.
    :type runid: str
    :param projectid: Project id of the asset.
    :type projectid: str
    :param meta: Asset meta.
    :type meta: dict[str, str]
    :param created_time: Time asset was created.
    :type created_time: datetime
    """

    _validation = {
        'name': {'required': True},
        'artifacts': {'required': True},
    }

    _attribute_map = {
        'id': {'key': 'id', 'type': 'str'},
        'name': {'key': 'name', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
        'artifacts': {'key': 'artifacts', 'type': '[Artifact]'},
        'tags': {'key': 'tags', 'type': '[str]'},
        'runid': {'key': 'runid', 'type': 'str'},
        'projectid': {'key': 'projectid', 'type': 'str'},
        'meta': {'key': 'meta', 'type': '{str}'},
        'created_time': {'key': 'createdTime', 'type': 'iso-8601'},
    }

    def __init__(self, name, artifacts, id=None, description=None, tags=None, runid=None, projectid=None, meta=None, created_time=None):
        super(Asset, self).__init__()
        self.id = id
        self.name = name
        self.description = description
        self.artifacts = artifacts
        self.tags = tags
        self.runid = runid
        self.projectid = projectid
        self.meta = meta
        self.created_time = created_time

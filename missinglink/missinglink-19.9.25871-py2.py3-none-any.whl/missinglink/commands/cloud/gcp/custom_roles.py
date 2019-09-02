# -*- coding: utf-8 -*-


class RmRole(object):
    ROLE_ID = 'missinglink_resource_management'

    TITLE = 'MissingLink Resource Management Service Account'

    DESCRIPTION = 'Handles MissingLink resources'

    PERMISSIONS = [
        "compute.networks.get",
        "compute.instances.list",
        "compute.instances.use",
        "compute.instances.stop",
        "compute.instances.start",
        "compute.instances.create",
        "compute.instances.delete",
        "compute.instances.setMetadata",
        "compute.machineTypes.list",
        "compute.disks.create",
        "compute.instances.get",
        "compute.projects.get",
        "compute.projects.setCommonInstanceMetadata",
        "compute.subnetworks.use",
        "compute.subnetworks.useExternalIp",
        'compute.instances.setServiceAccount',
        'compute.instances.setLabels',
        'compute.images.useReadOnly',
    ]


class InstancesRole(object):
    ROLE_ID = 'missinglink_instances'

    TITLE = 'MissingLink Instances Service Account'

    DESCRIPTION = 'Handles MissingLink instances'

    PERMISSIONS = [
        "storage.buckets.get",
        "storage.objects.create",
        "storage.objects.get",
        "storage.objects.list",
        "storage.objects.update",
        'cloudkms.cryptoKeyVersions.useToDecrypt',
    ]

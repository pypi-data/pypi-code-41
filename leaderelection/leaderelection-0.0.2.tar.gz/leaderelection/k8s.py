import os
import yaml
import time
import logging
from datetime import datetime
from kubernetes import client

logger = logging.getLogger(__name__)

def check_configmap(coreV1Api, namespace, configmap):
    cmaps = coreV1Api.list_namespaced_config_map(namespace)
    for cmap in cmaps.items:
        if cmap.metadata.name == configmap:
            return True
    return False

def get_configmap(coreV1Api, namespace, configmap):
    configmap = coreV1Api.read_namespaced_config_map(configmap, namespace)
    return configmap

def construct_configmap(configmap, namespace, pod):
    timestamp = datetime.now().isoformat()
    data = {
        'current-leader': pod,
        'timestamp': timestamp
    }
    metadata = client.V1ObjectMeta()
    metadata.name = configmap
    metadata.namespace = namespace
    cmap = client.V1ConfigMap()
    cmap.data = data
    cmap.metadata = metadata
    return cmap

def create_configmap(coreV1Api, namespace, configmap, pod):
    body = construct_configmap(configmap, namespace, pod)
    coreV1Api.create_namespaced_config_map(namespace, body)

def patch_configmap(coreV1Api, namespace, configmap, pod):
    body = construct_configmap(configmap, namespace, pod)
    coreV1Api.patch_namespaced_config_map(configmap, namespace, body)

def poll_configmap(coreV1Api, namespace, configmap, pod, pollDelaySeconds, leaseDurationSeconds):
    while True:
        time.sleep(pollDelaySeconds)
        timestamp = datetime.now().isoformat()
        cmap = get_configmap(coreV1Api, namespace, configmap)
        if cmap.data['current-leader'] == pod:
            # If we are the leader, update the timestamp in configmap
            patch_configmap(coreV1Api, namespace, configmap, pod)
        elif cmap.data['timestamp'] + timedelta(seconds=leaseDurationSeconds) < timestamp:
            # If timestamp in configmap + leaseDurationSeconds is less
            # than current timestamp, become the leader.
            patch_configmap(coreV1Api, namespace, configmap, pod)
        else:
            logger.info('{} is currently the leader. Polling for leader election'.format(cmap.data['current-leader']))

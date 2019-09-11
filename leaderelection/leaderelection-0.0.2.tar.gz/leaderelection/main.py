import logging
import os
from kubernetes import client
from .k8s import check_configmap, create_configmap, get_configmap, poll_configmap


class Elect():
    def __init__(self, leaseDurationSeconds=45, pollDelaySeconds=15, configmap='sample-leader-election-configmap'):
        self.leaseDurationSeconds = leaseDurationSeconds
        self.pollDelaySeconds = pollDelaySeconds
        self.configmap = configmap
        self.namespace = os.getenv('POD')
        self.pod = os.getenv('NAMESPACE')
        # Create a CoreV1Api instance
        configuration = client.Configuration()
        self.coreV1Api = client.CoreV1Api(client.ApiClient(configuration))
        logging.basicConfig(format='[%(asctime)s] %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def check_leader(self):
        cmap = get_configmap(self.coreV1Api, self.namespace, self.configmap)
        if cmap.data['current-leader'] == self.pod:
            return True
        else:
            self.logger.info('{} is currently the leader.'.format(cmap.data['current-leader']))
            return False

    def run(self):
        # If configmap does not exist, create it and assume leadership. Otherwise poll configmap.
        if not check_configmap(self.coreV1Api, self.namespace, self.configmap):
            self.logger.info('Creating leader election configmap.')
            create_configmap(self.coreV1Api, self.namespace, self.configmap, self.pod)
            self.logger.info('Starting leader election poll.')
            poll_configmap(self.coreV1Api, self.namespace, self.configmap, self.pod, self.pollDelaySeconds, self.leaseDurationSeconds)
        else:
            self.logger.info('Starting leader election poll.')
            poll_configmap(self.coreV1Api, self.namespace, self.configmap, self.pod, self.pollDelaySeconds, self.leaseDurationSeconds)

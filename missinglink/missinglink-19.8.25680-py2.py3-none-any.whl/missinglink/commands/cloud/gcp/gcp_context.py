# -*- coding: utf-8 -*-

import sys
import time
import logging
import json
import os
import re

import click
import six
import jinja2
import yaml
from retrying import retry

from missinglink.commands.cloud.backend_context import BackendContext
from .custom_roles import RmRole, InstancesRole


WAIT_EXPONENTIAL_MUL = 1000
WAIT_EXPONENTIAL_MAX = 5000


def should_retry(exception):
    from google.api_core.exceptions import ServiceUnavailable

    return type(exception) == ServiceUnavailable


class GcpContext(BackendContext):
    CLOUD_TYPE = 'gcp'

    DEFAULT_NETWORK = 'default'
    DEPLOYMENT_NAME = 'ml-deployment'
    GLOBAL_LOCATION = 'global'

    INSTANCES_SERVICE_ACCOUNT = 'ml-instances'

    SERVICE_ACCOUNT_USER_ROLE = 'roles/iam.serviceAccountUser'

    REQUIRED_APIS = {
        'compute.googleapis.com': 'Compute Engine API',
        'iam.googleapis.com': 'Identity and Access Management (IAM) API',
        'deploymentmanager.googleapis.com': 'Cloud Deployment Manager API',
        'cloudkms.googleapis.com': 'Cloud Key Management Service (KMS) API',
    }

    SLEEP_SEC = 10
    VALIDATE_APIS_TIMEOUT_SEC = 60 * 10

    KEYRING_ID = 'ml_keyring'
    CRYPTO_KEY_ID = 'ml_crypto_key'

    def __init__(self, ctx, kwargs):
        from googleapiclient import discovery as api

        super(GcpContext, self).__init__(ctx, kwargs)

        self.credentials = self._initialize_credentials()
        self.project_id = ctx.obj.gcp.project_id
        self.region = ctx.obj.gcp.region
        self.zone = ctx.obj.gcp.zone
        self.network_name = ctx.obj.gcp.network or self.DEFAULT_NETWORK
        self.boto_proxy_service_account = self.ctx.obj.config.rm_boto_proxy_svc_account
        self.storage_bucket = '{}_default'.format(self.org)

        self.auth_state = {'authorised': False, 'ssh_present': False}

        self.iam = api.build('iam', 'v1', credentials=self.credentials, cache_discovery=False)
        self.service_usage = api.build('serviceusage', 'v1', credentials=self.credentials, cache_discovery=False)
        self.cloud_resource_manager = api.build('cloudresourcemanager', 'v1', credentials=self.credentials,
                                                cache_discovery=False)
        self.deployment_manager = api.build('deploymentmanager', 'v2', credentials=self.credentials,
                                            cache_discovery=False)
        self.compute = api.build('compute', 'v1', credentials=self.credentials, cache_discovery=False)

        self.cloud_connector_data = {}
        self._initialize_cloud_data()

    def _initialize_credentials(self):
        from google.auth import default, exceptions
        from google.oauth2.credentials import Credentials

        credentials_file_path = self.kwargs.get('credentials_file_path')
        if credentials_file_path:
            credentials = Credentials.from_authorized_user_file(credentials_file_path)
            return credentials

        try:
            credentials, project_id = default()
        except exceptions.DefaultCredentialsError:
            msg = 'Cannot find Google cloud default credentials. ' \
                  'You can set them by running "gcloud auth application-default login", ' \
                  'or specify the location of your credentials file by adding the option ' \
                  '--credentials-file-path <path> to the command'
            raise click.ClickException(msg)

        return credentials

    def _initialize_cloud_data(self):
        self.cloud_connector_data['cloud_data'] = []

        self._add_cloud_data_key_data('queue', self.kwargs.pop('queue', None))
        self._add_cloud_data_key_data('project_id', self.project_id)
        self._add_cloud_data_key_data('region', self.region)
        if self.zone:
            self._add_cloud_data_key_data('zone', self.zone)

        rm_service_account = self._get_boto_proxy_service_account()
        self._add_cloud_data_key_data('rm_service_account', rm_service_account)
        instances_service_account = self._get_project_service_account_email(self.INSTANCES_SERVICE_ACCOUNT)
        self._add_cloud_data_key_data('instances_service_account', instances_service_account)

        self._add_cloud_data_key_data('gcs_buckets', json.dumps([self.storage_bucket]))

    def _add_cloud_data_key_data(self, key, data):
        self.cloud_connector_data['cloud_data'].append({'key': key, 'data': data})

    def init_and_authorise_app(self):
        click.echo('(2/9) Validating required APIs')
        self.authorize_apis()

        click.echo('(3/9) Validating network configuration')
        self.validate_network()

        click.echo('(4/9) Enabling Google APIs Service Agent to create roles')
        self.update_google_apis_service_account_permissions()

        click.echo('(5/9) Setting up KMS')
        self.setup_kms()

        self.process_existing_custom_roles()

        click.echo('(6/9) Setting up Missinglink deployment')
        self.setup_deployment()

        click.echo('(7/9) Setting instances service account roles')
        self.set_instances_service_account_roles()

        click.echo('(8/9) Authorizing MissingLink service account in project')
        self.authorize_boto_proxy_service_account()

        click.echo('(9/9) Configuring MissingLink backend integration')
        self.encrypt_and_send_connector()
        self.finalize_init()

        click.echo('GCP setup is done')

    def setup_deployment(self):
        deployment_config = self.generate_deployment()
        self.upsert_deployment(deployment_config)

        timeout = 60
        for _ in range(timeout):
            current_deployment = self._get_existing_deployment() or {}
            if current_deployment.get('operation', {}).get('progress') == 100:
                return

            time.sleep(self.SLEEP_SEC)

        raise click.ClickException('Missinglink deployment was not completed on time, please try to run init again')

    def process_existing_custom_roles(self):
        role_ids = (RmRole.ROLE_ID, InstancesRole.ROLE_ID)
        for role_id in role_ids:
            self._process_existing_custom_role(role_id)

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def _process_existing_custom_role(self, role_id):
        from googleapiclient import errors

        role_name = self._format_project_role(role_id)
        try:
            role = self.iam.projects().roles().get(name=role_name).execute()
        except errors.HttpError as exc:
            if exc.resp.status == 404:
                # the role does not exist
                return

            six.reraise(*sys.exc_info())

        if role.get('deleted'):
            etag = role['etag']
            body = {'etag': etag}
            click.echo('Enabling custom role {}, which already exists'.format(role_id))
            self.iam.projects().roles().undelete(name=role_name, body=body).execute()

    def _get_deployment_context(self):
        parameters = {
            'name': self.DEPLOYMENT_NAME,
            'project_id': self.project_id,
            'region': self.region,
            'stage': 'BETA',
            'rm_custom_role': {
                'roleId': RmRole.ROLE_ID,
                'title': RmRole.TITLE,
                'description': RmRole.DESCRIPTION,
                'includedPermissions': RmRole.PERMISSIONS,
            },
            'instances_custom_role': {
                'roleId': InstancesRole.ROLE_ID,
                'title': InstancesRole.TITLE,
                'description': InstancesRole.DESCRIPTION,
                'includedPermissions': InstancesRole.PERMISSIONS,
            },
            'instances_service_account': {
                'name': self.INSTANCES_SERVICE_ACCOUNT,
            },
            'storage': {
                'name': self.storage_bucket,
            },
        }

        return parameters

    def generate_deployment(self):
        parameters = self._get_deployment_context()
        templates_path = os.path.join(os.path.dirname(__file__))
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(templates_path))
        rendered_config = env.get_template('deployment_resources.jinja2').render(params=parameters)
        return yaml.load(rendered_config, Loader=yaml.FullLoader)

    def _get_existing_deployment(self):
        from googleapiclient import errors

        try:
            deployment = self.deployment_manager.deployments().get(project=self.project_id,
                                                                   deployment=self.DEPLOYMENT_NAME).execute()
            return deployment
        except errors.HttpError as exc:
            if exc.resp.status == 404:
                # the deployment does not exist
                return

            six.reraise(*sys.exc_info())

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def upsert_deployment(self, deployment_config):
        current_deployment = self._get_existing_deployment()

        deployment_body = {
            'name': self.DEPLOYMENT_NAME,
            'target': {
                'config': {
                    'content': json.dumps(deployment_config)
                }
            }
        }

        deployments = self.deployment_manager.deployments()

        if current_deployment:
            deployment_body['fingerprint'] = current_deployment['fingerprint']
            action = deployments.update(project=self.project_id, deployment=self.DEPLOYMENT_NAME, body=deployment_body)
        else:
            action = deployments.insert(project=self.project_id, body=deployment_body)

        action.execute()

    def _get_full_service_name(self, api_name):
        return 'projects/{}/services/{}'.format(self.project_id, api_name)

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def _get_disabled_required_apis(self, apis):
        services = self.service_usage.services()

        disabled_apis = []

        for api_name in sorted(apis):
            service_name = self._get_full_service_name(api_name)
            service = services.get(name=service_name).execute()
            if service['state'] != 'ENABLED':
                disabled_apis.append(api_name)

        return disabled_apis

    def _wait_for_apis_to_be_enabled(self, apis):
        click.echo("Waiting for APIs to complete enabling successfully")

        for _ in range(int(self.VALIDATE_APIS_TIMEOUT_SEC / self.SLEEP_SEC)):
            still_disabled = self._get_disabled_required_apis(apis)
            if not still_disabled:
                return

            time.sleep(self.SLEEP_SEC)

        raise click.ClickException('The following APIs did not complete enabling process on time: {}, '
                                   'please try to run init again later'.format(still_disabled))

    def authorize_apis(self):
        disabled_apis = self._get_disabled_required_apis(self.REQUIRED_APIS)
        for api_name in disabled_apis:
            service_name = self._get_full_service_name(api_name)
            self.service_usage.services().enable(name=service_name).execute()
            click.echo("{} will now be enabled".format(self.REQUIRED_APIS[api_name]))

        if disabled_apis:
            self._wait_for_apis_to_be_enabled(disabled_apis)

    def _extract_network_from_self_link(self, network_self_link):
        network_match = re.search('.*/{project_id}/(.*)'.format(project_id=self.project_id), network_self_link)
        if not network_match:
            logging.error("Can't extract network from selfLink %s", network_self_link)
            raise click.ClickException("Invalid GCP network response")

        return network_match.group(1)

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def validate_network(self):
        from googleapiclient import errors

        try:
            network = self.compute.networks().get(network=self.network_name, project=self.project_id).execute()
        except errors.HttpError as exc:
            if exc.resp.status == 403:
                msg = 'Permission error: {}'.format(exc.content)
                raise click.ClickException(msg)

            if exc.resp.status == 404:
                msg = 'Invalid network {}'.format(self.network_name)
                raise click.ClickException(msg)

            six.reraise(*sys.exc_info())

        subnets = network.get('subnetworks')

        network_path = self._extract_network_from_self_link(network['selfLink'])

        self._add_cloud_data_key_data('network', network_path)
        self._add_cloud_data_key_data('subnets', json.dumps(subnets))

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def setup_kms(self):
        from google.cloud import kms_v1

        keyring_id = self.KEYRING_ID
        client = kms_v1.KeyManagementServiceClient(credentials=self.credentials)
        parent = client.location_path(self.project_id, self.GLOBAL_LOCATION)
        crypto_key_id = self.CRYPTO_KEY_ID

        key_ring_response = self._ensure_keyring_exists(client, parent, keyring_id)

        key_response = self._ensure_crypto_key_exists(client, key_ring_response.name, crypto_key_id)

        self.cloud_connector_data['key'] = key_response.name

    def _ensure_keyring_exists(self, client, parent, keyring_id):
        from google.cloud import exceptions

        keyring_name = client.key_ring_path(self.project_id, self.GLOBAL_LOCATION, keyring_id)
        keyring = {'name': keyring_name}

        try:
            return client.create_key_ring(parent=parent, key_ring_id=keyring_id, key_ring=keyring, timeout=30)
        except exceptions.Conflict:
            return client.get_key_ring(keyring_name)

    @staticmethod
    def _ensure_crypto_key_exists(client, keyring_parent, crypto_key_id):
        from google.cloud import exceptions
        from google.cloud.kms_v1.gapic import enums

        purpose = enums.CryptoKey.CryptoKeyPurpose.ENCRYPT_DECRYPT
        rotation_period = 60 * 60 * 24 * 7  # one week
        next_rotation_time = int(time.time()) + rotation_period
        crypto_key_configuration = {
            'purpose': purpose,
            'next_rotation_time': {'seconds': next_rotation_time},
            'rotation_period': {'seconds': rotation_period},
        }

        try:
            return client.create_crypto_key(parent=keyring_parent, crypto_key_id=crypto_key_id,
                                            crypto_key=crypto_key_configuration)
        except exceptions.Conflict:
            # The key already exists
            return client.get_crypto_key('{}/cryptoKeys/{}'.format(keyring_parent, crypto_key_id))

    def update_cloud_connector(self, key, value):
        self.cloud_connector_data[key] = value

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def get_iam_policies(self):
        policy = self.cloud_resource_manager.projects().getIamPolicy(resource=self.project_id, body={}).execute()
        return policy

    @staticmethod
    def add_member_to_roles(policy, member, roles):

        def get_current_role_binding(_role):
            return next(b for b in bindings if b['role'] == _role)

        def process_role(_role):
            existing_roles = [b['role'] for b in bindings]
            if _role not in existing_roles:
                bindings.append({'role': _role, 'members': [member]})
                return

            current_role_binding = get_current_role_binding(_role)
            if member not in current_role_binding['members']:
                current_role_binding['members'].append(member)

        bindings = policy['bindings']
        for role in roles:
            process_role(role)

        return policy

    @staticmethod
    def _get_google_apis_service_account(current_policy):

        def get_google_svc_account_from_policy():
            all_members = {m for b in current_policy['bindings'] for m in b['members']}
            _google_service_accounts = [m for m in all_members if m.endswith('@cloudservices.gserviceaccount.com')]
            return _google_service_accounts

        google_service_accounts = get_google_svc_account_from_policy()
        if not google_service_accounts:
            # this should not happen
            logging.error('cloudservices.gserviceaccount.com not found in project members')
            raise click.ClickException('Unable to allow Google APIs Service Agent to create roles')

        return google_service_accounts[0]

    @retry(retry_on_exception=should_retry, wait_exponential_multiplier=WAIT_EXPONENTIAL_MUL,
           wait_exponential_max=WAIT_EXPONENTIAL_MAX)
    def _add_roles_to_service_account(self, service_account, roles):
        current_policy = self.get_iam_policies()
        updated_policy = self.add_member_to_roles(current_policy, service_account, roles)
        self.cloud_resource_manager.projects().setIamPolicy(
            resource=self.project_id, body={
                'policy': updated_policy
            }).execute()

    def update_google_apis_service_account_permissions(self):
        current_policy = self.get_iam_policies()
        google_service_accounts = self._get_google_apis_service_account(current_policy)
        roles = ['roles/iam.roleAdmin']
        self._add_roles_to_service_account(google_service_accounts, roles)

    def _get_project_service_account_email(self, service_account_name):
        return '{}@{}.iam.gserviceaccount.com'.format(service_account_name, self.project_id)

    def _format_service_account(self, service_account_name):
        return 'serviceAccount:{}'.format(self._get_project_service_account_email(service_account_name))

    def _format_project_role(self, role_name):
        return 'projects/{}/roles/{}'.format(self.project_id, role_name)

    def _get_boto_proxy_service_account(self):
        return 'serviceAccount:{}'.format(self.boto_proxy_service_account)

    def set_instances_service_account_roles(self):
        service_account = self._format_service_account(self.INSTANCES_SERVICE_ACCOUNT)
        roles = [self._format_project_role(InstancesRole.ROLE_ID)]
        self._add_roles_to_service_account(service_account, roles)

    def authorize_boto_proxy_service_account(self):
        service_account = self._get_boto_proxy_service_account()
        roles = [
            self._format_project_role(RmRole.ROLE_ID),
            self.SERVICE_ACCOUNT_USER_ROLE,
        ]
        self._add_roles_to_service_account(service_account, roles)

    def _init_prepare_connector_message(self, crypto_key_path, set_ssh, set_ml):
        kms = self.get_kms(crypto_key_path, self.credentials)
        template = self._prepare_cloud_connector_template(kms, set_ssh, set_ml, self.project_id)

        template.update(self.cloud_connector_data)
        logging.debug('Sending cloud connector with values: %s', template)

        self._post_cloud_connector(template)

    def encrypt_and_send_connector(self):
        self._prompt_for_ssh_if_needed()
        crypto_key_path = self.cloud_connector_data['key']
        self._init_prepare_connector_message(crypto_key_path, set_ssh=True, set_ml=True)

    def finalize_init(self):
        url = '{org}/gcp/finalize_init'.format(org=self.org)
        self._handle_api_call('post', url)

    @classmethod
    def get_kms(cls, crypto_key_path, credentials=None):
        from missinglink.crypto import GcpEnvelope

        return GcpEnvelope(crypto_key_path, credentials)

    @classmethod
    def validate_region_and_zone(cls, region, zone):
        def both_not_provided():
            return not region and not zone

        def both_provided():
            return region and zone

        def zone_not_in_region():
            return cls.extract_region_from_zone(zone) != region

        if both_not_provided():
            raise click.ClickException('Must provide region and/or zone')

        if both_provided() and zone_not_in_region():
            raise click.ClickException('Zone {} does not belong to region {}'.format(zone, region))

    @classmethod
    def extract_region_from_zone(cls, zone):
        return zone[:-2]

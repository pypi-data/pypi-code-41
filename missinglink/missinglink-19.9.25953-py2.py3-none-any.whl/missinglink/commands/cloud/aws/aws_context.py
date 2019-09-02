# -*- coding: utf-8 -*-
import logging
import uuid
from time import sleep

import click
from click import exceptions
from six.moves.urllib import parse

from missinglink.commands.cloud.backend_context import BackendContext
from missinglink.commands.utilities import TupleArray
from .cloud_formation import Cf
from .iam import Iam
from .sts import Sts


class AwsContext(BackendContext):
    CLOUD_TYPE = 'aws'

    def __init__(self, ctx, kwargs):
        BackendContext.__init__(self, ctx, kwargs)

        self.sts = Sts(ctx.obj.aws, self.org)
        self.whoami = self.sts.whoami()
        self.account_id = self.whoami['Account']
        self.region = self.ctx.obj.aws.region
        logging.debug('Org: %s, AWS account id: %s', self.org, self.account_id)
        self.auth_state = None
        self.refresh_auth_state()
        self.cf = Cf(self.ctx.obj.aws, self.org)

    def refresh_auth_state(self):
        self.auth_state = self._handle_api_call('get', '{}/aws/authorisation_status/{}'.format(self.org, self.account_id))
        logging.info('AWS auth status', self.auth_state)
        if self.auth_state.get('auth_region') is not None and self.ctx.obj.aws.region is None:
            self.region = self.auth_state.get('auth_region')
            self.ctx.obj.aws.region = self.region
            logging.info('AWS region changed to %s', self.region)
        return self.auth_state

    def encrypt_and_send_connector(self):
        if self._authorised_and_configured():
            return

        self._prompt_for_ssh_if_needed()
        self._authorise_if_needed()
        kms_arn = self.auth_state.pop('encryption_key', None)
        if not kms_arn:
            raise click.exceptions.ClickException('You are authorised but have no KMS key configured. Please contact MissingLinkAi')

        self._init_prepare_connector_message(kms_arn, set_ssh=not self.auth_state['ssh_present'], set_ml=not self.auth_state['mali_config'])

        self.refresh_auth_state()

    def _authorise_if_needed(self):
        if not self.auth_state['authorised']:
            self._ensure_role_absent()
            self._update_org_metadata_ssh_key(self.kwargs['ssh_public'])
            parameters = {'SshPublicKey': self.kwargs['ssh_public']}
            queue = self.kwargs.pop('queue', None)
            if queue:
                parameters['Queue'] = queue
            return self._get_submit_and_register_template('authorise_cf', 'ML-AUTH', parameters=parameters)

    def _ensure_role_absent(self):
        iam = Iam(self.ctx.obj.aws, self.org)
        ml_role_name = 'MissingLinkResourceManager-{org}'.format(org=self.org)
        cur_role = iam.get_role(ml_role_name)
        if cur_role is not None:
            logging.info('_has_auth_stack: stack present %s', cur_role)
            raise exceptions.ClickException('Role %s already exists in your AWS account. Role ID: %s. Please contact MissingLinkAi' % (ml_role_name, cur_role['Role']['RoleId']))

    @property
    def normalised_org_name(self):
        return self.org.replace('_', '-')

    def _get_submit_and_register_template(self, cf_command, stack_name, parameters=None):
        stack_name = '{}-{}'.format(stack_name, self.normalised_org_name)
        self._ensure_stack_absent(stack_name)

        result = self._handle_api_call('get', '{}/aws/{}/{}'.format(self.org, cf_command, self.account_id))
        logging.debug(result)
        tags = TupleArray.tuple_array_do_dict(result['tags'], key='key', value='value')
        template = result['template']
        offer_id = result['offering_id']
        cf_response = self.cf.create(stack_name, stack_data=template, tags=tags, parameters=parameters)
        stack_id = cf_response['StackId']
        self._handle_api_call('put', '{}/aws/register_cf_stack/{}/{}?{}'.format(self.org, self.account_id, offer_id, parse.urlencode({'stack': stack_id})), {})
        self._wait_stack_for_complete(stack_name)
        self.refresh_auth_state()

    def _ensure_stack_absent(self, stack_name):
        cur_stack = self.cf.get(stack_name)
        if cur_stack is not None:
            logging.info('_has_stack_name: stack present %s', cur_stack)
            raise exceptions.ClickException('%s stack already exists in your AWS account with State: %s. Please contact MissingLinkAi' % (stack_name, cur_stack['status']))

    def _wait_stack_for_complete(self, stack):
        from missinglink.commands.commons import output_result

        cur_stack = self.cf.get(stack)
        while not cur_stack['status'].lower().endswith('complete'):
            click.echo('%s: %s' % (stack, cur_stack['status']))
            resources = self.cf.resources(stack)
            output_result(self.ctx, resources)
            sleep(5)
            click.echo(chr(27) + "[2J")
            cur_stack = self.cf.get(stack)

        return self.cf.get(stack)

    @classmethod
    def get_kms(cls, kms_arn):
        from missinglink.crypto.legacy import KmsLegacyEnvelope

        return KmsLegacyEnvelope(kms_arn)

    def _init_prepare_connector_message(self, kms_key_arn, set_ssh, set_ml):
        kms = self.get_kms(kms_key_arn)

        template = self._prepare_cloud_connector_template(kms, set_ssh, set_ml, self.account_id)

        template['cloud_data'] = {}

        self._post_cloud_connector(template)

    def setup_spot_role_if_needed(self):
        iam = Iam(self.ctx.obj.aws, self.org)
        iam.verify_spot_role_exists()

    def setup_vpc_if_needed(self):

        if self._is_vpc_active():
            return

        self._get_submit_and_register_template('new_vpc_cf', 'ML-VPC')

    def _is_vpc_active(self):
        if not self.region:
            return len(self.auth_state.get('vpc_regions', [])) > 0

        return self.region is not None and self.region in self.auth_state.get('vpc_regions', [])

    def setup_s3_if_needed(self, force=False):

        if not force and int(self.auth_state.get('s3_count') or 0) > 0:
            return

        return self._get_submit_and_register_template('new_s3_cf', 'ML-S3-{}'.format(uuid.uuid4().hex[:3].lower()))

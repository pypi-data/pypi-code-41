import logging

import click

from missinglink.crypto import Asymmetric
from missinglink.commands.utilities import TupleArray
from missinglink.commands.utilities.click_utils import pop_key_or_prompt_if
from missinglink.commands.utilities.docker_tools import DockerTools
from missinglink.commands.utilities.path_tools import PathTools
from .cloud_connector import CloudConnector


class BackendContext(object):
    CLOUD_TYPE = None

    def __init__(self, ctx, kwargs):
        self.org = kwargs['org']
        self.ctx = ctx
        self.kwargs = kwargs
        self.auth_state = None

    def change_local_server(self, server, new_group):
        return self._handle_api_call('put', '{}/resource/{}/change_local_group'.format(self.org, server), {'group': new_group})

    def create_queue(self, name, updates):
        updates['display'] = name
        return self._queue_action(name, method='post', updates=updates)

    def update_queue(self, name, updates):
        return self._queue_action(name, method='put', updates=updates)

    def get_queue(self, name):
        return self._queue_action(name, method='get')

    def _queue_action(self, queue_id, method='get', updates=None):
        url = '{}/queue/{}'.format(self.org, queue_id)
        return self._handle_api_call(method, url, data=updates)

    @classmethod
    def b64encode_name(cls, group_name):
        return Asymmetric.bytes_to_b64str(group_name.encode('utf-8'))

    def resource_group_description(self, group_id):
        group_description = self._handle_api_call('get', '{}/aws/resource_group/{}?b64name=True'.format(self.org, self.b64encode_name(group_id)))

        return {k.pop('key'): k for k in group_description['data']}

    def put_resource_group_parameters(self, group_id, params, new_cloud_type=None):
        data = TupleArray.dict_to_tuple_array(params, key='key', value='values')
        is_new = new_cloud_type is not None
        if not is_new:
            new_cloud_type = 'all'
        group_description = self._handle_api_call(
            'post' if is_new else 'put',
            '{}/{}/resource_group/{}?b64name=True'.format(self.org, new_cloud_type, self.b64encode_name(group_id)),
            data={'params': data})

        return {k.pop('key'): k for k in group_description['data']}

    def _handle_api_call(self, method, url, data=None):
        from missinglink.core.api import ApiCaller

        return ApiCaller.call(self.ctx.obj, self.ctx.obj.session, method, url, data)

    def _update_org_metadata_ssh_key(self, ssh_key_pub):
        url = 'orgs/{org}/metadata'.format(org=self.org)

        metadata_request = {
            'metadata': [
                {
                    'name': 'ssh_public_key',
                    'value': ssh_key_pub,
                    'operation': 'REPLACE'
                }
            ]
        }
        self._handle_api_call('post', url, metadata_request)

    @classmethod
    def encrypt(cls, kms, data):
        return kms.convert_encrypted_envelope_data_to_triple(kms.encrypt(data))

    @classmethod
    def decrypt(cls, kms, data):
        if len(data) == 3:
            iv, key, en_data = data
            return kms.decrypt(kms.convert_triple_to_encrypted_envelope_data({'iv': iv, 'key': key, 'data': en_data}))

    def get_kms(self, kms_key):
        raise NotImplemented()

    def _prepare_cloud_connector_template(self, kms, set_ssh, set_ml, connector_id):
        template, config_data = CloudConnector.cloud_connector_defaults(self.ctx, cloud_type=self.CLOUD_TYPE,
                                                                        kwargs=dict(connector=connector_id))
        if set_ssh:
            ssh_key_path = pop_key_or_prompt_if(self.kwargs, 'ssh_key_path', text='SSH key path [--ssh-key-path]',
                                                default=PathTools.get_ssh_path())
            ssh_key = DockerTools.export_key_from_path(ssh_key_path)
            ssh = self.encrypt(kms, ssh_key)
            template['ssh'] = ssh

        if set_ml:
            mali = self.encrypt(kms, config_data)
            template['mali'] = mali

        return template

    def _post_cloud_connector(self, template):
        url = '{org}/cloud_connector/{name}'.format(org=self.org, name=template['name'])
        response = self._handle_api_call('post', url, template)
        logging.debug('_post_cloud_connector response: %s', response)

    def _prompt_for_ssh_if_needed(self):
        if self.auth_state['authorised'] and self.auth_state['ssh_present']:
            return

        self._pre_apply_default_ssh_key()
        has_key = False
        while not has_key:
            has_key = self._try_read_key()

    def _try_read_key(self):
        from missinglink.crypto import SshIdentity

        try:
            self.kwargs['ssh_key_path'] = pop_key_or_prompt_if(self.kwargs, 'ssh_key_path', text='SSH key path [--ssh-key-path]', default=PathTools.get_ssh_path())
            ssh_key = SshIdentity(self.kwargs['ssh_key_path'])
            self.kwargs['ssh_private'] = ssh_key.export_private_key_bytes().decode('utf-8')
            self.kwargs['ssh_public'] = ssh_key.export_public_key_bytes().decode('utf-8')
            return True

        except Exception as e:
            click.echo('Failed to read ssh key from %s. Please check the path and try again. %s' % (self.kwargs['ssh_key_path'], str(e)))
            self.kwargs.pop('ssh_key_path')
        return False

    def _authorised_and_configured(self):
        return self.auth_state['authorised'] and self.auth_state['ssh_present'] and self.auth_state['mali_config']

    def _pre_apply_default_ssh_key(self):
        if self.kwargs.get('ssh_key_path') is None:
            self.kwargs['ssh_key_path'] = PathTools.get_ssh_path()
            logging.info('Using %s as default ssh path', self.kwargs['ssh_key_path'])

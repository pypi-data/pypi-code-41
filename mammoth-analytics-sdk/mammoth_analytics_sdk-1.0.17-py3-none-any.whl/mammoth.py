from __future__ import unicode_literals

import logging
import time
import traceback
import random

import requests
from MammothAnalytics import const
from MammothAnalytics.const import USER_PERMISSIONS
from MammothAnalytics.errors import AuthError, UnknownError
from MammothAnalytics.errors import MalformedRequestError, AuthenticationError, \
    NotFoundError, AuthorizationError
from .urls import get_url
import pydash

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)


def handleError(f):
    def new_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (AuthError, UnknownError, NotFoundError, AuthenticationError,
                AuthorizationError, MalformedRequestError) as e:
            raise e
        except Exception as e:
            fname = f.__name__
            log.error({
                'function_name': fname,
                'args': args,
                'kwrgs': kwargs
            })
            log.error(''.join(traceback.format_exc()))
            raise UnknownError(0, 'Error in: {0}'.format(fname))

    new_function.__name = f.__name__
    new_function.__doc__ = f.__doc__
    return new_function


class MammothConnector(object):
    def __init__(self, email, password=None, account_id=None, token=None, api_url=None):

        """
        The main class for handling Mammoth Analytics API
        :param email: The email of the user
        :param password: The password of the user
        :param account_id: Account ID. If not given now, it can be given after `select accounts`
        """
        if not api_url:
            api_url = const.API
        self.api_url = api_url
        self.__account_id = None

        if token:
            self.__token = token
        elif password:
            response = requests.post(get_url('/login', self.api_url), json=dict(email=email, password=password, is_long_term=True))
            if response.status_code != 200:
                raise AuthError(response.json()["ERROR_CODE"],'{0}'.format(response.status_code, response.json()['ERROR_MESSAGE']))
            self.__token = response.json()['token']
            response = requests.post(get_url('/login', self.api_url), json=dict(email=email, password=password, is_long_term=True))
            if response.status_code != 200:
                raise AuthError("username or password is not correct")
            self.__token = response.json()['token']
        else:
            raise AuthError("Token or Password needed!")

        if account_id is not None:
            self.select_account(account_id)
        else:
            self.auto_select_account()
        log.info("Logged in as {0} into account {1}".format(email, self.__account_id))

    def __del__(self):
        try:
            if self.__token:
                self.logout()
        except:
            pass

    def _make_signed_request(self, rtype, api, **kwargs):
        log.info((rtype, api))
        headers = {'X-API-KEY': self.__token}
        if self.__account_id:
            headers['X-ACCOUNT-ID'] = str(self.__account_id)
        if 'headers' in kwargs.keys():
            kwargs['headers'].update(headers)
        else:
            kwargs['headers'] = headers
        method_maps = {
            'get': requests.get,
            'post': requests.post,
            'delete': requests.delete,
            'patch': requests.patch
        }
        api_url = get_url(api, self.api_url)
        response = method_maps[rtype](api_url, **kwargs)
        resp = {'ERROR_CODE': 0, 'ERROR_MESSAGE': 'Unknown'}
        try:
            resp = response.json()
            log.debug('response json :{0}'.format(resp))
        except Exception as e:
            raise UnknownError(resp['ERROR_CODE'], 'Server responded with status code :{0}'.format(response.status_code, resp['ERROR_MESSAGE']))
        if response.status_code == 200:
            return response
        elif response.status_code == 500:
            if resp['ERROR_CODE'] == 0:
                raise UnknownError(resp['ERROR_CODE'], 'Server responded with status code :{0} and message:'.format(response.status_code, resp['ERROR_MESSAGE']))
        else:
            exc_class = UnknownError
            if response.status_code == 400:
                exc_class = MalformedRequestError
            elif response.status_code == 401:
                exc_class = AuthenticationError
            elif response.status_code == 403:
                exc_class = AuthorizationError
            elif response.status_code == 404:
                exc_class = NotFoundError
            raise exc_class(resp['ERROR_CODE'], resp['ERROR_MESSAGE'])

    @handleError
    def list_accounts(self):
        """
        Returns a list of accounts user has access to
        :return: List of dictionaries. Each dictionary contains id, name and other properties associated with an account
        """
        response = self._make_signed_request('get', '/accounts')
        return response.json()['accounts']

    @handleError
    def list_users(self):
        """
        Returns a list of accounts user has access to
        :return: List of dictionaries. Each dictionary contains id, name and other properties associated with an account
        """
        response = self._make_signed_request('get', '/accounts/{account_id}/users'.format(account_id=self.__account_id))
        return response.json()['users']

    @handleError
    def select_account(self, account_id):
        """
        Sets the account id on the class. This is important to use any other method in the class
        :param account_id: Account id to be selected
        :return: None
        """
        accounts = self.list_accounts()
        account_ids = [a['id'] for a in accounts]
        log.info("Account id list {0}".format(account_ids))
        if account_id in account_ids:
            self.__account_id = account_id
        else:
            raise AuthError(0, "Account ID is not valid")

    @handleError
    def auto_select_account(self):
        """
        selects the first account in the list of accounts the user belongs to
        """
        accounts = self.list_accounts()
        self.select_account(accounts[0]['id'])

    @handleError
    def logout(self):
        """
        Will log out from Mammoth. This is also done automatically when the object is garbage collected.
        :return:
        """
        self._make_signed_request('post', '/logout', json={})

    @handleError
    def add_user_to_account(self, email, full_name, user_permission=USER_PERMISSIONS.ANALYST,
                            get_access_token=False):
        log.info("Account id is {0}".format(self.__account_id))
        response = self._make_signed_request('post', '/accounts/{account_id}/users'.format(account_id=self.__account_id),
                                             json={
                                                 'email': email,
                                                 'full_name': full_name,
                                                 'perm_name': user_permission,
                                                 'get_access_token': get_access_token
                                             })
        return response.json()

    @handleError
    def remove_user_from_account(self, user_id):
        self._make_signed_request('delete', '/accounts/{account_id}/users/{user_id}'.format(
            account_id=self.__account_id, user_id=user_id
        ))

    @handleError
    def list_datasets(self):
        """
        Returns a list of datasets in the system
        :return: List of dictionaries containing info about the datasets in the system. Contains info such as id, name etc.
        """
        response = self._make_signed_request('get', '/datasets')
        return response.json()['datasets']

    @handleError
    def refresh_dataset(self, ds_id):
        response = self._make_signed_request('patch', '/dataset/{0}'.format(ds_id), json={
            "patch": [{"op": "replace", "path": "data", "value": "refresh"}]})
        return response.json()

    @handleError
    def delete_dataset(self, ds_id):
        response = self._make_signed_request('delete', '/datasets/{0}'.format(ds_id))
        return response.json()

    @handleError
    def delete_identity(self, identity_key, integration_key):
        response = self._make_signed_request('delete', '/integrations/{0}/identities/{1}'.format(integration_key, identity_key))
        return response.json()

    @handleError
    def create_dataset(self, name, metadata, display_properties=None):
        """
        Create a dataset in Mammoth Analytics.

        TODO: explain metadata and display properties somewhere and put links here

        :param name: Name of the dataset
        :param metadata: Metadata for the given dataset. This is a list of dict objects. Each dict should contain `display_name`,
            `internal_name` and `type`. `type` should be one of `NUMERIC`, `TEXT` or `DATE`
        :param display_properties: A dictionary of display properties.
        :return: Datasource id
        """
        if not display_properties:
            display_properties = {'FORMAT_INFO': {}, "SORT": []}
        response = self._make_signed_request(
            'post', '/datasets',
            json={'name': name, 'metadata': metadata,
                  'display_properties': display_properties})
        return response.json()['id']

    @handleError
    def create_webhook_dataset(self, name, is_secure=False):
        """
        Create a webhook dataset in Mammoth Analytics.
        :param name: Name of the dataset
        :return: Datasource id
        """

        webhook_ds_param = {"name": name, "origins": "*", "is_secure": is_secure}
        response = self._make_signed_request(
            'post', '/webhooks',
            json=webhook_ds_param)
        return response.json()

    @handleError
    def get_webhook_by_uri(self, webhook_uri):
        webhook_details = None
        all_webhooks = self.list_webhooks()
        for wh in all_webhooks:
            if wh.get('url') == webhook_uri:
                webhook_details = wh
                break
        return webhook_details

    @handleError
    def list_webhooks(self):
        response = self._make_signed_request('get', 'webhooks').json()
        webhooks = response.get('webhooks', [])
        return webhooks

    @handleError
    def post_data_to_webhook(self, uri, data):
        if not isinstance(uri, basestring):
            raise TypeError("webhook uri should be of string type. found {0} instead".format(type(uri)))
        return self._make_signed_request('post', uri, json=data)

    @handleError
    def get_dataset(self, ds_id):
        """
        Returns a dataset information dictionary for the given ID
        :param ds_id: The datasource id
        :return: dictionary containing information on the dataset
        """
        response = self._make_signed_request('get', '/datasets/{0}'.format(ds_id))
        return response.json()

    @handleError
    def get_task(self, view_id):
        response = self._make_signed_request('get', '/workspaces/{0}/tasks'.format(view_id))
        return response.json().get('tasks')

    @handleError
    def add_task(self, view_id, params, wait_till_ready=True):
        response = self._make_signed_request('post', '/workspaces/{0}/tasks'.format(view_id), json={'param': params})
        if wait_till_ready:
            self._wait_till_request_is_complete_get_data(view_id, response.json()['request_id'])
        return response

    @handleError
    def update_task(self, view_id, task_id, params, wait_till_ready=True):
        response = self._make_signed_request('patch', '/workspaces/{0}/tasks/{1}'.format(view_id, task_id),
                                             json={"patch": [{"op": "replace", "path": "params", "value": params}]})
        if wait_till_ready:
            self._wait_till_request_is_complete_get_data(view_id, response.json()['request_id'])
        return response.json()

    @handleError
    def delete_task(self, view_id, task_id, wait_till_ready=True):
        response = self._make_signed_request('delete', '/workspaces/{0}/tasks/{1}'.format(view_id,task_id))
        if wait_till_ready:
            self._wait_till_request_is_complete_get_data(view_id, response.json()['request_id'])

        return response

    @handleError
    def refresh_webhook_data(self, webhook_id):
        response = self._make_signed_request('post', 'webhooks/{0}'.format(webhook_id))
        return response.json()
    @handleError
    def get_task_statuses(self, view_id):
        response = self._make_signed_request('get', 'workspaces/{0}/task-statuses'.format(view_id))
        return response.json().get('statuses')

    @handleError
    def add_data_to_dataset(self, ds_id, data, end_batch=False):
        """
        Add data to a dataset as a list of dictionaries.

        :param ds_id: The target dataset id
        :param data: a list of dictionaries. Each dictionary represents a row of data where key is the column internal name and value is the value of the cell.
        :param end_batch: If true , this would be considered an end of batch.
        :return: A processing response dictionary
        """
        response = self._make_signed_request('post', '/datasets/{0}/data'.format(ds_id),
                                             json={"rows": data, "endBatch": end_batch})
        return response.json()

    @handleError
    def add_data_to_dataset_as_csv(self, ds_id, file_path, has_header):
        """
        To add clean data to a dataset as a csv. Should contain a csv that has the same structure has the metadata.
        use this only if you are sure that all the rows of the right format. That is, each row should contain comma
        separated values in the same order as dataset metadata

        :param has_header: If the file has a header row.
        :param ds_id: the destination ds id
        :param file_path: the path of the file where you want to upload
        """
        header_string = 'true'
        if not has_header:
            header_string = 'false'
        files = {'file': open(file_path, 'rb')}
        response = self._make_signed_request('post', '/datasets/{0}/data'.format(ds_id),
                                             files=files, data={"has_header": header_string})
        return response.json()

    @handleError
    def upload_csv(self, file_path, target_datasource_id=None, replace=False):
        """
        To upload an arbitrary csv file to the system. The system would return a file id based on which one can track
        the progress of the file through the mammoth system.

        :param file_path: The file path
        :param target_datasource_id: if this is set to a dataset id, the arbitrary csv would be appended to the
            data of the dataset.
        :return: A file id.
        """
        files = {'file': open(file_path, 'rb')}
        post_data = {}
        if target_datasource_id:
            post_data = {'append_to_ds_id': target_datasource_id}
            if replace:
                post_data['replace'] = "true"
        response = self._make_signed_request('post', '/files', files=files, data=post_data)
        log.info(response.json())
        return response.json()['id']

    @handleError
    def append_datasets(self, source_dataset_id, target_dataset_id, column_mapping):
        params = {
            "source": "datasource",
            "source_id": source_dataset_id,
            "mapping": column_mapping
        }
        response = self._make_signed_request('post', '/datasets/{0}/batches'.format(target_dataset_id), json=params)
        log.info(response.json())
        return response.json()

    def wait_till_file_processing_get_ds(self, file_id):
        """
        Method will wait till the file with given id has finished processing. Works only for csv files right now.
        TODO: Write logic to support excel, zip files.
        :param file_id:
        :return: A dataset dictionary
        """
        while True:
            response = self._make_signed_request('get', '/files/{0}'.format(file_id))
            file_info = response.json()['file']
            status = file_info['status']
            if status != 'processing':
                log.info(file_info)
                break
            else:
                time.sleep(1)
        response = self._make_signed_request('get', '/files/{0}'.format(file_id))
        file_info = response.json()['file']
        final_ds_id = file_info["additional_data"].get("final_ds_id")
        append_to_ds_id = file_info["additional_data"].get("append_to_ds_id")
        self._wait_for_ds_status(final_ds_id, 'processing', check_for_status_equality=False)
        if append_to_ds_id:
            self._wait_for_ds_status(append_to_ds_id, 'ready')
            ds = self.get_dataset(append_to_ds_id)
        else:
            ds = self.get_dataset(final_ds_id)
        return ds

    @handleError
    def _wait_for_ds_status(self, ds_id, status, check_for_status_equality=True):
        while ds_id and True:
            ds = self.get_dataset(ds_id)
            ds_status = ds['status']
            if check_for_status_equality:
                if ds_status == status:
                    break
                else:
                    time.sleep(1)
            else:
                if ds_status != status:
                    break
                else:
                    time.sleep(1)

    @handleError
    def get_ds_for_file(self, file_id):
        """
        Will return the dataset for the given file.
        :param file_id: The file id
        :return: A ds information dictionary
        """
        datasets = self.list_datasets()
        for i in range(len(datasets)):
            ds = datasets[len(datasets) - 1 - i]
            if 'source_id' in list(ds.keys()):
                if ds['source_id'] == file_id and ds['source_type'] == 'file':
                    return ds

    @handleError
    def list_views(self, ds_id):
        """
        Returns a list of views a dataset has
        :param ds_id: Dataset ID
        :return: list of workspace dictionaries
        """
        response = self._make_signed_request('get', '/datasets/{0}/workspaces'.format(ds_id))
        return response.json()['workspaces']

    @handleError
    def create_view(self, ds_id, duplicate_from_view_id=None):
        """
        Returns a list of views a dataset has
        :param ds_id: Dataset ID
        :return: list of workspace dictionaries
        """
        params = {}
        if duplicate_from_view_id:
            params['clone_config_from'] = duplicate_from_view_id
        response = self._make_signed_request('post', '/datasets/{0}/workspaces'.format(ds_id), json=params)
        return response.json()['workspace_id']

    @handleError
    def run_transform(self, view_id, param):
        r = self._make_signed_request('post', '/workspaces/{0}/tasks'.format(view_id), json={'param': param})
        return r.json()

    @handleError
    def get_view_details(self, view_id):
        r = self._make_signed_request('get', '/workspaces/{0}'.format(view_id))
        return r.json()

    @handleError
    def wait_till_view_is_ready(self, view_id):
        while True:
            time.sleep(1)
            view = self.get_view_details(view_id)
            if view['status'] == 'ready':
                break

    @handleError
    def copy_template_from_view(self, ds_id, view_id):
        """
        use this method to copy template from another view and apply to the dataset's view. If the dataset has an
        empty view, it will be reused. Else, a new view will get created.

        :param ds_id: The dataset id
        :param view_id: The view ID from which you want to copy the template from.
        :return: Nothing
        """
        self._make_signed_request('post',
                                  '/datasets/{0}/workspaces'.format(ds_id),
                                  json={'clone_config_from': view_id})

    @handleError
    def _run_action(self, view_id, param, wait_till_ready=False ):
        """
        Runs an action.
        :param view_id: The view on which the action is to be performed
        :param param: The param for the action.
        :return: Request Id for the action
        """
        r = self._make_signed_request('post', '/workspaces/{0}/actions'.format(view_id), json={'param': param})
        if wait_till_ready:
            self._wait_till_request_is_complete_get_data(view_id, r.json()['request_id'])
        return r.json()['request_id']

    @handleError
    def edit_action(self, view_id,action_id, param, wait_till_ready=False):
        """
        edit an action.
        :param view_id: The view on which the action is to be performed
        :param action_id:The param to get applied action id
        :param param: The param for the action.
        :return: Request Id for the action
        """

        r = self._make_signed_request('patch', '/workspaces/{0}/actions/{1}'.format(view_id, action_id), json={"patch": [{"op": "replace", "path": "params", "value": param}]})
        if wait_till_ready:
            self._wait_till_request_is_complete_get_data(view_id, r.json()['request_id'])
        return r.json()['request_id']

    def _wait_till_request_is_complete_get_data(self, view_id, request_id):
        while True:
            time.sleep(1)
            r = self._make_signed_request('get',
                                          '/workspaces/{0}/requests/{1}'.format(view_id, request_id))
            data = r.json()
            if data['status'] in ['success', 'failure', 'referror']:
                return data

    @handleError
    def list_actions(self, view_id):
        response = self._make_signed_request('get', '/workspaces/{0}/actions'.format(view_id))
        log.debug("List actions : {0}".format(response))
        return response.json()['triggers']

    @handleError
    def push_view_data_to_mysql(self, view_id, host, username, password, port, database, target_table=None):
        action_param = {
            'run_immediately': True,
            # 'validate_only': True,
            'target_properties': {
                'username': username,
                'password': password,
                'database': database,
                'host': host,
                'table': target_table,
                'port': port
            },
            'trigger_type': 'none',
            'additional_properties': {},
            'handler_type': 'mysql'
        }
        request_id = self._run_action(view_id, action_param)
        self._wait_till_request_is_complete_get_data(view_id, request_id)

    @handleError
    def download_view_as_csv(self, view_id, file_prefix=None, condition=None):
        if not isinstance(file_prefix, str):
            file_prefix ='file_{0}'.format(random.randint(1000, 2000))
        # action_param = {
        #     "handler_type":"s3",
        #     "trigger_type":"none",
        #     "run_immediately":True,
        #     "additional_properties":{
        #         "email_notifications": {
        #             "on": False
        #         }
        #     },
        #     "WORKSPACE_ID":view_id,
        #     "CONDITION":condition,
        #     "target_properties":{
        #         "use_format":True,
        #         "include_hidden":False,
        #         "file_prefix": file_prefix
        #     }
        # }
        action_param = {
            "handler_type": "s3",
            "trigger_type": "none",
            "run_immediately": True,
            "sequence": None,
            "additional_properties": {},
            "WORKSPACE_ID": view_id,
            "target_properties": {
                "file":file_prefix,
                "use_format":True,
                "include_hidden": False
             }
        }
        request_id = self._run_action(view_id, action_param)
        self._wait_till_request_is_complete_get_data(view_id, request_id)
        notifications = self.list_notifications()
        for n in notifications:
            url = pydash.get(n, 'details.data.additional_data.url')
            if isinstance(url, str):
                if file_prefix in url:
                    return url

    @handleError
    def list_notifications(self):
        r = self._make_signed_request('get', '/resources')
        data = r.json()
        return data['notifications']['items']

    @handleError
    def _get_async_request_data(self, request_id):
        url = '/async/{0}'.format(request_id)
        r = self._make_signed_request('get', url)
        return r.json()

    @handleError
    def add_third_party_identity(self, integration_key, identity_config):
        url = '/integrations/{0}/identities'.format(integration_key)
        r = self._make_signed_request('post', url, json=identity_config)
        request_id = r.json()['request_id']
        while True:
            time.sleep(2)
            data = self._get_async_request_data(request_id)
            if data['STATUS'] == 'SUCCESS':
                return data['response']['identity_key']
            elif data['STATUS'] == 'PROCESSING':
                continue
            else:
                raise AuthError(data['message'])

    @handleError
    def get_third_party_identity_key_by_name(self, integration_key, name):
        url = "/integrations/{0}/identities".format(integration_key)
        r = self._make_signed_request('get', url)
        data = r.json()
        for identity in data['identities']:
            if identity['name'] == name:
                return identity['value']

    @handleError
    def get_third_party_identities(self, integration_key):
        url = "/integrations/{0}/identities".format(integration_key)
        r = self._make_signed_request('get', url)
        data = r.json()
        return data['identities']

    @handleError
    def validate_third_party_ds_config(self, integration_key, identity_key, ds_config):
        url = '/integrations/{0}/identities/{1}/dsConfigs'.format(integration_key, identity_key)
        r = self._make_signed_request('post', url, json=ds_config)
        data = r.json()
        return data['is_valid']

    @handleError
    def create_third_party_dataset(self, ds_param, wait_till_ready=False):
        url = '/datasets'
        r = self._make_signed_request('post', url, json=ds_param)
        data = r.json()
        ds_id = data['datasource_id']
        if wait_till_ready:
            self.wait_till_ds_ready(ds_id)
        return ds_id

    def wait_till_ds_ready(self, ds_id):
        while True:
            datasets = self.list_datasets()
            ds_ready = False
            for i in range(len(datasets)):
                ds = datasets[len(datasets) - 1 - i]
                log.info(ds)
                if ds['id'] == ds_id:
                    if ds['status'] == 'processing':
                        time.sleep(2)
                        continue
                    if ds['status'] in ['ready', 'error']:
                        time.sleep(1)
                        ds_ready = True
                        break
                    log.info(ds['status'])
            if ds_ready:
                break

    @handleError
    def apply_template_to_view(self, view_id, template_config, wait_till_ready=False):
        url = '/workspaces/{0}/exportable-config'.format(view_id)
        r = self._make_signed_request('post', url, json={"config": template_config})
        data = r.json()

        if wait_till_ready:
            time.sleep(5)
            self.wait_till_view_is_ready(view_id)
        return data['STATUS'] == 'PROCESSING'

import json
from argparse import ArgumentParser

import requests
import jsonschema

from red_connector_xnat.schemas import SEND_FILE_SCHEMA, RECEIVE_FILE_SCHEMA
from red_connector_xnat.helpers import auth_method_obj, graceful_error


RECEIVE_FILE_DESCRIPTION = 'Receive input file from XNAT via HTTP(S).'
RECEIVE_FILE_VALIDATE_DESCRIPTION = 'Validate access data for receive-file.'

SEND_FILE_DESCRIPTION = 'Send output file to XNAT via HTTP(S).'
SEND_FILE_VALIDATE_DESCRIPTION = 'Validate access data for send-file.'


def _receive_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)

    auth_method = auth_method_obj(access)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    base_url = access['baseUrl'].rstrip('/')
    project = access['project']
    subject = access.get('subject')
    session = access.get('session')
    container_type = access.get('containerType')
    container = access.get('container')
    resource = access['resource']
    file = access['file']

    url = '{}/REST/projects/{}/resources/{}/files/{}'.format(
        base_url, project, resource, file
    )

    if subject is not None:
        url = '{}/REST/projects/{}/subjects/{}/resources/{}/files/{}'.format(
            base_url, project, subject, resource, file
        )

    if session is not None:
        url = '{}/REST/projects/{}/subjects/{}/experiments/{}/resources/{}/files/{}'.format(
            base_url, project, subject, session, resource, file
        )

    if container_type is not None:
        url = '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}'.format(
            base_url, project, subject, session, container_type, container, resource, file
        )

    r = requests.get(
        url,
        auth=auth_method,
        verify=verify,
        stream=True
    )
    r.raise_for_status()

    with open(local_file_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)
    r.raise_for_status()

    cookies = r.cookies

    r = requests.delete(
        '{}/data/JSESSION'.format(base_url),
        cookies=cookies,
        verify=verify
    )
    r.raise_for_status()


def _receive_file_validate(access):
    with open(access) as f:
        access = json.load(f)

    jsonschema.validate(access, RECEIVE_FILE_SCHEMA)


def _send_file(access, local_file_path):
    with open(access) as f:
        access = json.load(f)

    auth_method = auth_method_obj(access)

    verify = True
    if access.get('disableSSLVerification'):
        verify = False

    base_url = access['baseUrl'].rstrip('/')
    project = access['project']
    subject = access['subject']
    session = access['session']
    container_type = access['containerType']
    container = access['container']
    resource = access.get('resource', 'OTHER')
    xsi_type = access.get('xsiType')
    file = access['file']
    overwrite_existing_file = access.get('overwriteExistingFile')

    r = requests.get(
        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}?format=json'.format(
            base_url, project, subject, session, container_type
        ),
        auth=auth_method,
        verify=verify
    )
    r.raise_for_status()
    existing_containers = r.json()['ResultSet']['Result']
    cookies = r.cookies

    try:
        container_exists = False
        existing_xsi_type = None

        for ec in existing_containers:
            if ('ID' in ec and ec['ID'] == container) or ('label' in ec and ec['label'] == container):
                container_exists = True
                existing_xsi_type = ec['xsiType']
                break

        if not container_exists:
            # create container
            container_url = '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}'.format(
                base_url, project, subject, session, container_type, container
            )

            if xsi_type:
                container_url = '{}?xsiType={}'.format(container_url, xsi_type)

            r = requests.put(
                container_url,
                cookies=cookies,
                verify=verify
            )
            r.raise_for_status()

            # create file
            with open(local_file_path, 'rb') as f:
                r = requests.put(
                    '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                        base_url, project, subject, session, container_type, container, resource, file
                    ),
                    data=f,
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()

        else:
            if xsi_type and xsi_type != existing_xsi_type:
                raise Exception(
                    'xsiType "{}" of existing container "{}" does not match provided xsiType "{}"'.format(
                        existing_xsi_type, container, xsi_type))

            r = requests.get(
                '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources?format=json'.format(
                    base_url, project, subject, session, container_type, container
                ),
                cookies=cookies,
                verify=verify
            )
            r.raise_for_status()
            existing_resources = r.json()['ResultSet']['Result']

            resource_exists = False
            for er in existing_resources:
                if ('ID' in er and er['ID'] == resource) or ('label' in er and er['label'] == resource):
                    resource_exists = True
                    break

            if not resource_exists:
                # create file
                with open(local_file_path, 'rb') as f:
                    r = requests.put(
                        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                            base_url, project, subject, session, container_type, container, resource, file
                        ),
                        data=f,
                        cookies=cookies,
                        verify=verify
                    )
                    r.raise_for_status()

            else:
                r = requests.get(
                    '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files?format=json'.format(
                        base_url, project, subject, session, container_type, container, resource
                    ),
                    cookies=cookies,
                    verify=verify
                )
                r.raise_for_status()
                existing_files = r.json()['ResultSet']['Result']

                file_exists = False
                for ef in existing_files:
                    if 'Name' in ef and ef['Name'] == file:
                        file_exists = True
                        break

                if file_exists:
                    if not overwrite_existing_file:
                        raise Exception(
                            'File "{}" already exists and overwriteExistingFile is not set.'.format(file)
                        )
                    # delete file
                    r = requests.delete(
                        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}'.format(
                            base_url, project, subject, session, container_type, container, resource, file
                        ),
                        cookies=cookies,
                        verify=verify
                    )
                    r.raise_for_status()

                # create file
                with open(local_file_path, 'rb') as f:
                    r = requests.put(
                        '{}/REST/projects/{}/subjects/{}/experiments/{}/{}/{}/resources/{}/files/{}?inbody=true'.format(
                            base_url, project, subject, session, container_type, container, resource, file
                        ),
                        data=f,
                        cookies=cookies,
                        verify=verify
                    )
                    r.raise_for_status()
    except Exception:
        # delete session
        r = requests.delete('{}/data/JSESSION'.format(base_url), cookies=cookies, verify=verify)
        r.raise_for_status()
        raise

    # delete session
    r = requests.delete('{}/data/JSESSION'.format(base_url), cookies=cookies, verify=verify)
    r.raise_for_status()


def _send_file_validate(access):
    with open(access) as f:
        access = json.load(f)
    
    jsonschema.validate(access, SEND_FILE_SCHEMA)


@graceful_error
def receive_file():
    parser = ArgumentParser(description=RECEIVE_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local input file path.'
    )
    args = parser.parse_args()
    _receive_file(**args.__dict__)


@graceful_error
def receive_file_validate():
    parser = ArgumentParser(description=RECEIVE_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _receive_file_validate(**args.__dict__)


@graceful_error
def send_file():
    parser = ArgumentParser(description=SEND_FILE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    parser.add_argument(
        'local_file_path', action='store', type=str, metavar='LOCALFILE',
        help='Local output file path.'
    )
    args = parser.parse_args()
    _send_file(**args.__dict__)


@graceful_error
def send_file_validate():
    parser = ArgumentParser(description=SEND_FILE_VALIDATE_DESCRIPTION)
    parser.add_argument(
        'access', action='store', type=str, metavar='ACCESSFILE',
        help='Local path to ACCESSFILE in JSON format.'
    )
    args = parser.parse_args()
    _send_file_validate(**args.__dict__)

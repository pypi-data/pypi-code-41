"""NamedTuple and (basically) setters/getters used in secretctl cli"""
import json
import sys
from typing import NamedTuple
import boto3
from botocore.exceptions import ClientError

class Secret(NamedTuple):
    """immutable secret class for working with AWS Secrets Manager"""
    path: str
    value: str = None
    description: str = None
    tags: list = None
    versions: list = None

Secret.__doc__ = "Secret: namedtuple for Secret object in secretctl"
Secret.path.__doc__ = "[Name,SecretId] path/to/secret/key"
Secret.value.__doc__ = "[SecretString] secret value (SecretBinary not yet supported)"
Secret.description.__doc__ = "[Description] a description of the secret"
Secret.tags.__doc__ = "[Tags] tags in form of [{ \"Key\": \"<tag name>\", \"Value\": \"<tag value>\"}]"
Secret.versions.__doc__ = "[Versions] from list_secret_version_ids()"

_session = boto3.session.Session().client(service_name='secretsmanager', region_name='us-east-1')

def create_secret(path, value, description=None, tags=None):
    """create path:value in AWS Secrets Manager"""
    secret_kwargs = {}
    try:
        secret_kwargs['Name'] = path
        secret_kwargs['SecretString'] = value
        if description:
            secret_kwargs['Description'] = description
        if tags:
            secret_kwargs['Tags'] = tags
        resp = _session.create_secret(**secret_kwargs)
        return Secret(path=resp['Name'])
    except ClientError as e:
        # use secretctl update to change existing secrets
        print(e)
        sys.exit(1)

def get_secret(path):
    #pylint: disable=R1260
    """get path from from AWS Secrets Manager"""
    secret_kwargs = {}
    try:
        secret_kwargs['path'] = path
        resp = _session.describe_secret(SecretId=path)
        if 'Description' in resp:
            secret_kwargs['description'] = resp['Description']
        if 'Tags' in resp:
            secret_kwargs['tags'] = resp['Tags']
        resp = _session.get_secret_value(SecretId=path)
        if 'SecretString' in resp:
            secret_kwargs['value'] = json.loads(resp['SecretString'])
        secret_kwargs['versions'] = len(_session.list_secret_version_ids(SecretId=path)['Versions'])
        return Secret(**secret_kwargs)
    except ClientError as e:
        print(e)
        sys.exit(1)

def update_secret(path, value, description=None):
    """modify secret (causing new version), update description and/or tags"""
    secret_kwargs = {}
    try:
        resp = _session.describe_secret(SecretId=path)
        secret_kwargs['SecretId'] = path
        secret_kwargs['SecretString'] = value
        resp = _session.put_secret_value(**secret_kwargs)
        if description:
            secret_kwargs['Description'] = description
            resp = _session.update_secret(**secret_kwargs)
        return Secret(path=resp['Name'])
    except ClientError as e:
        print(e)
        sys.exit(1)

# removed from code coverage pending moto support for mocking secretsmanager tags
def tag_secret(path, tags=None):  # pragma: no cover
    """add tags to secret"""
    secret_kwargs = {}
    secret_kwargs['SecretId'] = path
    secret_kwargs['Tags'] = tags
    try:
        _session.tag_resource(**secret_kwargs)
        return Secret(path=path)
    except ClientError as e:
        print(e)
        sys.exit(1)

# removed from code coverage pending moto support for mocking secretsmanager tags
def untag_secret(path, tags=None):  # pragma: no cover
    """remove tags from secret"""
    secret_kwargs = {}
    secret_kwargs['SecretId'] = path
    secret_kwargs['TagKeys'] = tags
    try:
        _session.untag_resource(**secret_kwargs)
        return Secret(path=path)
    except ClientError as e:
        print(e)
        sys.exit(1)

def list_secrets():
    """list all secrets"""
    _secrets = []
    paginator = _session.get_paginator('list_secrets')
    page_iterator = paginator.paginate()
    for page in page_iterator:
        _secrets += page['SecretList']
    return _secrets

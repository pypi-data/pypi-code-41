#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# IDE: PyCharm 2017.2.4
# Author: Dajiang Ren<rendajiang@gagogroup.com>
# Created on 2018-06-13


import os
from datetime import datetime

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from gagoos.storage import StorageService, \
    Object, \
    Bucket, \
    ObjectNotExistsError, \
    ObjectExistsError, \
    StorageClassType, \
    StorageClassTypeError, \
    ACLError, \
    ACLType


_storage_class_type_mapping = {
    StorageClassType.Standard: 'STANDARD',
    StorageClassType.InfrequentAccess: 'ONEZONE_IA',
    StorageClassType.Archive: 'GLACIER'
}


def _get_real_storage_class(storage_class: str) -> str:
    if storage_class in _storage_class_type_mapping:
        return _storage_class_type_mapping[storage_class]
    else:
        raise StorageClassTypeError()


_acl_mapping = {
    ACLType.PublicRead: 'public-read',
    ACLType.Private: 'private',
    ACLType.PublicReadWrite: 'public-read-write',
    ACLType.AuthenticatedRead: 'authenticated-read'
}


def _get_real_acl(acl: str) -> str:
    if acl in _acl_mapping:
        return _acl_mapping[acl]
    else:
        raise ACLError()


class S3Object(Object):
    def __init__(
            self,
            client,
            bucket_name: str,
            object_name: str,
            size: int,
            e_tag: str,
            last_modified: datetime
    ):
        super().__init__(bucket_name, object_name, size, e_tag, last_modified)
        self.client = client

    def _download_to_file(
            self,
            local_file_path: str,
            requester_pay: bool = False
    ):
        if requester_pay:
            self.client.download_file(
                Bucket=self.bucket_name,
                Key=self.object_name,
                Filename=local_file_path,
                ExtraArgs={
                    'RequestPayer': 'requester'
                }
            )
        else:
            self.client.download_file(
                Bucket=self.bucket_name,
                Key=self.object_name,
                Filename=local_file_path
            )

    def get_url(self):
        return '%s/%s/%s' % (self.client.meta.endpoint_url, self.bucket_name, self.object_name)

    def get_vsi_gdal_url(self):
        return '/vsis3/%s/%s' % (
            self.bucket_name,
            self.object_name
        )

    def get_data(self, requester_pay: bool = False):
        if requester_pay:
            res = self.client.get_object(
                Bucket=self.bucket_name,
                Key=self.object_name,
                RequestPayer='requester'
            )
        else:
            res = self.client.get_object(
                Bucket=self.bucket_name,
                Key=self.object_name
            )
        body: StreamingBody = res['Body']
        return body.read()

    def read_data(
            self,
            from_range: int,
            to_range: int,
            requester_pay: bool=False
    ) -> bytes or None:
        if requester_pay:
            res = self.client.get_object(
                Bucket=self.bucket_name,
                Key=self.object_name,
                RequestPayer='requester',
                Range='bytes=%d-%d' % (
                    from_range,
                    to_range
                )
            )
        else:
            res = self.client.get_object(
                Bucket=self.bucket_name,
                Key=self.object_name,
                Range='bytes=%d-%d' % (
                    from_range,
                    to_range
                )
            )
        body: StreamingBody = res['Body']
        return body.read()


class S3Bucket(Bucket):
    def __init__(self, client, bucket_name: str):
        super().__init__(bucket_name)
        self.client = client

    def get_object(self, object_name: str, requester_pay=False) -> S3Object or None:
        if self.exist(object_name, requester_pay):
            if requester_pay:
                header: dict = self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    RequestPayer='requester'
                )
            else:
                header: dict = self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                )
            return S3Object(
                self.client,
                self.bucket_name,
                object_name,
                header['ContentLength'],
                header['ETag'],
                header['LastModified']
            )
        else:
            raise ObjectNotExistsError

    def get_object_list(self, prefix: str = None, requester_pay=False) -> list:
        paginator = self.client.get_paginator('list_objects')
        objects: list = list()
        resume_token: str = None
        while True:
            if prefix is None:
                if requester_pay:
                    result = paginator.paginate(Bucket=self.bucket_name,
                                                RequestPayer='requester',
                                                PaginationConfig={'MaxItems': 1000,
                                                                  'PageSize': 1000,
                                                                  'StartingToken': resume_token})
                else:
                    result = paginator.paginate(Bucket=self.bucket_name,
                                                PaginationConfig={'MaxItems': 1000,
                                                                  'PageSize': 1000,
                                                                  'StartingToken': resume_token})
            else:
                if requester_pay:
                    result = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix,
                                                RequestPayer='requester',
                                                PaginationConfig={'MaxItems': 1000,
                                                                  'PageSize': 1000,
                                                                  'StartingToken': resume_token})
                else:
                    result = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix,
                                                PaginationConfig={'MaxItems': 1000,
                                                                  'PageSize': 1000,
                                                                  'StartingToken': resume_token})
            for r in result:
                if 'Contents' in r:
                    contents: dict = r['Contents']
                else:
                    contents = list()
                if len(contents) == 0:
                    break
                for content in contents:
                    obj: S3Object = S3Object(self.client, self.bucket_name, content['Key'], content['Size'],
                                             content['ETag'], content['LastModified'])
                    objects.append(obj)
            resume_token = result.resume_token
            if not resume_token:
                break
        return objects

    def get_object_data(self, object_name: str, requester_pay=False):
        if self.exist(object_name):
            if requester_pay:
                res = self.client.get_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    RequestPayer='requester'
                )
            else:
                res = self.client.get_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
            body: StreamingBody = res['Body']
            return body.read()
        else:
            raise ObjectNotExistsError

    def upload_file(
            self,
            local_file_path: str,
            object_name: str,
            acl: str = ACLType.Private,
            overwrite_if_exists: bool = True,
            storage_class_type: str = StorageClassType.Standard
    ) -> S3Object:
        if not self.exist(object_name) or overwrite_if_exists:
            self.client.upload_file(
                local_file_path,
                self.bucket_name,
                object_name,
                ExtraArgs={
                    'StorageClass': _get_real_storage_class(storage_class_type)
                }
            )
        else:
            raise ObjectExistsError
        self.client.put_object_acl(
            Bucket=self.bucket_name,
            Key=object_name,
            ACL=_get_real_acl(acl)
        )
        header: dict = self.client.head_object(
            Bucket=self.bucket_name,
            Key=object_name
        )
        return S3Object(
            self.client,
            self.bucket_name,
            object_name,
            header['ContentLength'],
            header['ETag'],
            header['LastModified']
        )

    def upload_data(
            self, data: bytes,
            object_name: str,
            acl: str = ACLType.Private,
            overwrite_if_exists: bool = True,
            storage_class_type: str = StorageClassType.Standard
    ) -> S3Object:
        if not self.exist(object_name) or overwrite_if_exists:
            self.client.put_object(
                ACL=_get_real_acl(acl),
                Body=data,
                Bucket=self.bucket_name,
                Key=object_name,
                ContentLength=len(data),
                StorageClass=_get_real_storage_class(storage_class_type)
            )
        else:
            raise ObjectExistsError
        header: dict = self.client.head_object(
            Bucket=self.bucket_name,
            Key=object_name
        )
        return S3Object(
            self.client,
            self.bucket_name,
            object_name,
            header['ContentLength'],
            header['ETag'],
            header['LastModified']
        )

    def exist(
            self,
            object_name: str,
            requester_pay: bool = False
    ):
        try:
            if requester_pay:
                self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    RequestPayer='requester'
                )
            else:
                self.client.head_object(
                    Bucket=self.bucket_name,
                    Key=object_name
                )
            return True
        except ClientError as error:
            if error.response['Error']['Code'] == '404':
                return False

    def remove(self, object_name: str):
        if self.exist(object_name):
            self.client.delete_object(
                Bucket=self.bucket_name,
                Key=object_name
            )

    def batch_remove(self, object_names: list):
        for i in range(0, len(object_names), 1000):
            names: list = list()
            for o_n in object_names[i:i + 1000]:
                names.append({'Key': o_n})
            self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={'Objects': names}
            )

    def rename(
            self,
            object_name: str,
            new_object_name: str,
            acl: str = ACLType.Private
    ):
        if self.exist(object_name):
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': object_name
            }
            self.client.copy(
                copy_source,
                Bucket=self.bucket_name,
                Key=new_object_name
            )
            self.client.put_object_acl(
                Bucket=self.bucket_name,
                Key=new_object_name,
                ACL=_get_real_acl(acl)
            )
            self.remove(object_name)


class S3StorageService(StorageService):
    def __init__(
            self,
            auth_first: str,
            auth_second: str,
            region: str,
            proxies: dict = None,
            requester_pay: bool = None
    ):
        super().__init__(
            auth_first,
            auth_second,
            proxies,
            requester_pay
        )
        self.client = boto3.client(
            's3',
            aws_access_key_id=auth_first,
            aws_secret_access_key=auth_second,
            region_name=region,
            config=Config(proxies=proxies)
        )

    def _get_bucket_impl(self, bucket_name: str, proxies: dict = None) -> Bucket:
        return S3Bucket(self.client, bucket_name)


def create_service(
        first: str,
        second: str,
        region: str = "cn-north-1",
        proxies: dict = None,
        requester_pay: bool = None
):
    return S3StorageService(first, second, region, proxies, requester_pay)


def get_object_url(
        region: str,
        bucket_name: str,
        object_name: str,
):
    return os.path.join(
        'https://s3.%s.amazonaws.com.cn/%s' % (
            region,
            bucket_name
        ),
        object_name
    )


if __name__ == '__main__':
    s: S3StorageService = S3StorageService('AKIAPZKG6ANJSGGNTDSQ', 'UUNXCjb3KNiJp0rpEN9qDi02Oj73Xf5STLdaQKmo',
                                           'cn-northwest-1')
    b = s.exist('gagostore', 'abc')
    s.upload_file('gagostore', 'storage1.py', 's3.py', 'public-read')
    aaa = s.get_data('gagostore', 'storage1.py')
    sss = s.get_data_as_text('gagostore', 'storage1.py')
    os: list = s.get_object_list('gagostore', 'storage')
    dd = 1

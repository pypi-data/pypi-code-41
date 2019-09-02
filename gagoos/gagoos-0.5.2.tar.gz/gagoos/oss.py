#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# IDE: PyCharm 2017.2.4
# Author: Dajiang Ren<rendajiang@gagogroup.com>
# Created on 2018-06-14


from datetime import datetime
from urllib.parse import urlparse

import oss2

from gagoos.storage import StorageService, \
    Bucket, \
    Object, \
    ObjectNotExistsError, \
    ObjectExistsError, \
    ACLType, \
    ACLError, \
    StorageClassType, \
    StorageClassTypeError

_acl_mapping = {
    ACLType.Private: oss2.OBJECT_ACL_PRIVATE,
    ACLType.PublicRead: oss2.OBJECT_ACL_PUBLIC_READ,
    ACLType.PublicReadWrite: oss2.OBJECT_ACL_PUBLIC_READ_WRITE,
    ACLType.AuthenticatedRead: oss2.OBJECT_ACL_PRIVATE
}


def _get_real_acl(acl: str):
    if acl in _acl_mapping:
        return _acl_mapping[acl]
    else:
        raise ACLError()


_storage_class_mapping = {
    StorageClassType.Standard: 'Standard',
    StorageClassType.InfrequentAccess: 'IA',
    StorageClassType.Archive: 'Archive'
}


def _get_real_storage_class(storage_class: str) -> str:
    if storage_class in _storage_class_mapping:
        return _storage_class_mapping[storage_class]
    else:
        raise StorageClassTypeError()


class OSSObject(Object):
    def __init__(self, bucket: oss2.Bucket, object_name: str, size: int, e_tag: str, last_modified: datetime):
        super().__init__(bucket.bucket_name, object_name, size, e_tag, last_modified)
        self.bucket: oss2.Bucket = bucket

    def _download_to_file(
            self,
            local_file_path: str,
            requester_pay: bool = False
    ):
        self.bucket.get_object_to_file(self.object_name, local_file_path)

    def get_url(self):
        url_split = urlparse(self.bucket.endpoint)
        return 'https://%s.%s/%s' % (self.bucket_name, url_split[1], self.object_name)

    def get_vsi_gdal_url(self):
        return '/vsioss/%s/%s' % (
            self.bucket_name,
            self.object_name
        )

    def get_data(
            self,
            requester_pay: bool = False
    ):
        object_stream = self.bucket.get_object(
            self.object_name
        )
        result: bytes = object_stream.read()
        if object_stream.client_crc != object_stream.server_crc:
            raise ValueError('CRC check failed when get data from OSS')
        return result

    def read_data(
            self,
            from_range: int,
            to_range: int,
            requester_pay: bool = False
    ) -> bytes or None:
        object_stream = self.bucket.get_object(
            self.object_name,
            byte_range=(
                from_range,
                to_range
            )
        )
        return object_stream.read()


class OSSBucket(Bucket):
    def __init__(self, auth: oss2.Auth, region: str, bucket_name: str):
        super().__init__(bucket_name)
        self.bucket: oss2.Bucket = oss2.Bucket(auth, region, bucket_name)

    def get_object(
            self,
            object_name: str,
            requester_pay: bool = False
    ) -> OSSObject:
        if self.exist(object_name):
            try:
                meta: oss2.models.GetObjectMetaResult = self.bucket.get_object_meta(object_name)
            except oss2.exceptions.NoSuchKey:
                raise ObjectNotExistsError
            return OSSObject(self.bucket, object_name, meta.content_length, meta.etag,
                             datetime.fromtimestamp(meta.last_modified))
        else:
            raise ObjectNotExistsError

    def get_object_list(
            self,
            prefix: str = None,
            requester_pay: bool = False
    ) -> list:
        marker: str = ''
        objects: list = list()
        while True:
            results: oss2.models.ListObjectsResult = self.bucket.list_objects(prefix=prefix, marker=marker,
                                                                              max_keys=1000)
            for r in results.object_list:
                object_info: oss2.models.SimplifiedObjectInfo = r
                objects.append(OSSObject(self.bucket, object_info.key, object_info.size, object_info.etag,
                                         datetime.fromtimestamp(object_info.last_modified)))
            marker = results.next_marker
            if not marker:
                break
        return objects

    def upload_file(
            self,
            local_file_path: str,
            object_name: str,
            acl: str,
            overwrite_if_exists: bool = True,
            storage_class_type: str = StorageClassType.Standard
    ):
        if not self.exist(object_name) or overwrite_if_exists:
            self.bucket.put_object_from_file(
                object_name,
                local_file_path,
                headers={
                    'x-oss-storage-class': _get_real_storage_class(
                        storage_class_type
                    ),
                    'x-oss-object-acl': _get_real_acl(acl)
                }
            )
            return self.get_object(object_name)
        else:
            raise ObjectExistsError

    def upload_data(
            self,
            data: bytes,
            object_name: str,
            acl: str,
            overwrite_if_exists: bool = True,
            storage_class_type: str = StorageClassType.Standard
    ):
        if not self.exist(object_name) or overwrite_if_exists:
            self.bucket.put_object(
                object_name,
                data,
                headers={
                    'x-oss-storage-class': _get_real_storage_class(
                        storage_class_type
                    ),
                    'x-oss-object-acl': _get_real_acl(acl)
                }
            )
            return self.get_object(object_name)
        else:
            raise ObjectExistsError

    def exist(self, object_name: str, requester_pay: bool = False):
        return self.bucket.object_exists(object_name)

    def remove(self, object_name: str):
        if self.exist(object_name):
            self.bucket.delete_object(object_name)

    def batch_remove(self, object_names: list):
        for i in range(0, len(object_names), 1000):
            names: list = object_names[i:i + 1000]
            self.bucket.batch_delete_objects(names)

    def rename(self, object_name: str, new_object_name: str, acl: str = 'private'):
        if self.exist(object_name):
            self.bucket.copy_object(self.bucket_name, object_name, new_object_name)
            self.bucket.put_object_acl(new_object_name, acl)
            self.remove(object_name)


class OSSStorageService(StorageService):
    def __init__(
            self,
            auth_first: str,
            auth_second: str,
            region: str,
            proxies: dict = None,
            requester_pay=None
    ):
        super().__init__(
            auth_first,
            auth_second,
            proxies,
            requester_pay
        )
        self.auth = oss2.Auth(auth_first, auth_second)
        self.service = oss2.Service(self.auth, region)

    def _get_bucket_impl(
            self,
            bucket_name: str,
            proxies: dict = None
    ) -> OSSBucket:
        return OSSBucket(
            self.auth,
            self.service.endpoint,
            bucket_name
        )


def create_service(
        first: str,
        second: str,
        region: str = "https://oss-cn-hangzhou.aliyuncs.com",
        proxies: dict = None,
        requester_pay: bool = None
):
    return OSSStorageService(
        first,
        second,
        region,
        proxies,
        requester_pay
    )

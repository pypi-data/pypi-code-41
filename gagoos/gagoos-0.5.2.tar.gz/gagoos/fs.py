#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# IDE: PyCharm 2017.2.4
# Author: Dajiang Ren<rendajiang@gagogroup.com>
# Created on 2018-09-26

import os
import shutil
import datetime

from gagoos.storage import StorageService, \
    Bucket, \
    Object, \
    ObjectNotExistsError, \
    ObjectExistsError, \
    StorageClassType


class FileSystemObject(Object):
    def __init__(self, bucket_name: str, object_name: str, size: int, e_tag: str, last_modified: datetime.datetime,
                 directory: str):
        super().__init__(bucket_name, object_name, size, e_tag, last_modified)
        self.full_path = os.path.join(directory, object_name)

    def _download_to_file(self, local_file_path: str, requester_pay: bool = False):
        local_dir: str = os.path.dirname(local_file_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        shutil.copy(self.full_path, local_file_path)

    def get_data(self, request_pay: bool = False) -> bytes or None:
        with open(self.full_path, 'rb') as fp:
            return fp.read()

    def read_data(
            self,
            from_range: int,
            to_range: int,
            requester_pay: bool = False
    ) -> bytes or None:
        with open(
                self.full_path,
                'rb'
        ) as fp:
            fp.seek(from_range)
            return fp.read(to_range-from_range+1)

    def get_url(self):
        return self.full_path

    def get_gdal_url(self):
        return self.full_path

    def get_vsi_gdal_url(self):
        return self.full_path


class FileSystemBucket(Bucket):
    def __init__(self, bucket_name: str, root: str):
        super().__init__(bucket_name)
        self.directory = os.path.join(root, bucket_name)
        if self.directory and not os.path.exists(self.directory):
            os.makedirs(self.directory, exist_ok=True)

    def get_object_list(self, prefix: str = None, requester_pay=False) -> list:
        file_list = list()
        directory = os.path.join(self.directory, prefix)
        if os.path.exists(directory):
            files = os.listdir(directory)
            for f in files:
                full_path: str = os.path.join(
                    directory,
                    f
                )
                if os.path.isdir(full_path):
                    pass
                elif os.path.isfile(full_path):
                    file_list.append(
                        FileSystemObject(
                            self.bucket_name,
                            os.path.join(
                                prefix,
                                f
                            ),
                            os.path.getsize(full_path),
                            '',
                            datetime.datetime.fromtimestamp(
                                os.path.getmtime(full_path),
                                tz=datetime.timezone.utc
                            ),
                            self.directory
                        )
                    )
        return file_list

    def get_object(self, object_name: str, requester_pay=False) -> Object or None:
        if self.exist(object_name):
            full_path = os.path.join(self.directory, object_name)
            return FileSystemObject(self.bucket_name, object_name, os.path.getsize(full_path), '',
                                    os.path.getmtime(full_path), self.directory)

    def get_object_data(self, object_name: str, requester_pay=False) -> bytes or None:
        if self.exist(object_name):
            full_path = os.path.join(self.directory, object_name)
            file_object: FileSystemObject = FileSystemObject(
                self.bucket_name, object_name, os.path.getsize(full_path), '',
                os.path.getmtime(full_path), self.directory
            )
            return file_object.get_data()

    def upload_file(
            self,
            local_file_path: str,
            object_name: str,
            acl: str,
            overwrite_if_exists: bool = True,
            storage_class_type: str = StorageClassType.Standard
    ) -> Object:
        if not os.path.exists(local_file_path):
            raise FileNotFoundError
        if self.exist(object_name):
            if overwrite_if_exists:
                self.remove(object_name)
            else:
                raise ObjectExistsError
        dst_path = os.path.join(self.directory, object_name)
        dir_name = os.path.dirname(dst_path)
        os.makedirs(dir_name, exist_ok=True)
        shutil.copy(local_file_path, dst_path)
        return self.get_object(object_name)

    def upload_data(
            self,
            data: bytes,
            object_name: str,
            acl: str,
            overwrite_if_exists: bool = True,
            storage_class_type: str = StorageClassType.Standard
    ) -> Object:
        if self.exist(object_name):
            if overwrite_if_exists:
                self.remove(object_name)
            else:
                raise ObjectExistsError
        dst_path = os.path.join(self.directory, object_name)
        dir_name = os.path.dirname(dst_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(dst_path, 'wb') as fp:
            fp.write(data)
        return self.get_object(object_name)

    def exist(
            self,
            object_name: str,
            requester_pay: bool = False
    ) -> bool:
        full_path = os.path.join(self.directory, object_name)
        return os.path.exists(full_path)

    def remove(self, object_name: str):
        if self.exist(object_name):
            full_path = os.path.join(self.directory, object_name)
            os.remove(full_path)
        else:
            raise ObjectNotExistsError

    def batch_remove(self, object_names: list):
        for o_n in object_names:
            self.remove(o_n)

    def rename(self, object_name: str, new_object_name: str, acl: str = 'private'):
        if self.exist(object_name):
            src_path: str = os.path.join(self.directory, object_name)
            dst_path: str = os.path.join(self.directory, new_object_name)
            shutil.move(src_path, dst_path)
        else:
            raise ObjectNotExistsError


class FileSystemStorageService(StorageService):
    def __init__(
            self,
            first: str,
            second: str,
            region: str = '',
            proxies: dict = None,
            requester_pay: bool = None
    ):
        super().__init__(
            first,
            second,
            proxies,
            requester_pay
        )
        self.root = region

    def _get_bucket_impl(self, bucket_name: str):
        return FileSystemBucket(
            bucket_name,
            self.root
        )


def create_service(
        first: str,
        second: str,
        region: str = '',
        proxies: dict = None,
        requester_pay: bool = None
):
    return FileSystemStorageService(
        first,
        second,
        region,
        proxies,
        requester_pay
    )


def get_object_url(
        region: str,
        bucket_name: str,
        object_name: str,
):
    return os.path.join(
        region,
        bucket_name,
        object_name
    )


if __name__ == '__main__':
    f: StorageService = FileSystemStorageService('', '')
    b: Bucket = f.get_bucket('123')
    b.upload_file('s3.py', '123.py', acl='public', overwrite_if_exists=True)

# -*- coding: utf-8 -*-
from ..ml_base_object_store import _MlBaseObjectStore_AsyncExecute
from .cloud_object_store import CloudObjectStore
from ...gcs_utils import do_delete_all, Downloader, Uploader


class GCSObjectStore(CloudObjectStore, _MlBaseObjectStore_AsyncExecute):
    def __init__(self, connection, bucket_name):
        super(GCSObjectStore, self).__init__(connection)
        self.__bucket_name = bucket_name
        self.__volume_id = self._connection.data_volume_config.volume_id
        self.__storage_volume_id = self._connection.data_volume_config.storage_volume_id

    def delete_all(self, max_files=None):
        return do_delete_all(self.__bucket_name, self.__volume_id, max_files)

    def _gen_upload_sync_args(self, obj, progress_callback=None):
        object_name = self._get_shafile_path(obj.sha)

        content_type = obj.content_type
        headers = self._get_content_headers(content_type)

        object_name = '%s/%s' % (self.__storage_volume_id, object_name)

        return self.__bucket_name, object_name, obj.full_path, headers, progress_callback

    def _get_loose_object_data(self, object_name, target_fileobj=None, progress_callback=None):
        return Downloader.download_bucket(self.__bucket_name,
                                          object_name,
                                          target_fileobj=target_fileobj, progress_callback=progress_callback)

    def add_objects_async(self, objects, callback=None, progress_callback=None):
        self._add_objects_async_with_method(objects, Uploader.upload_bucket, callback, progress_callback=progress_callback)

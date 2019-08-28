# -*- coding: utf-8 -*-
import errno
import logging
import os
from contextlib import closing

import six
from missinglink.core.exceptions import NonRetryException
from missinglink.legit.dulwich.objects import hex_to_filename, Blob
from missinglink.legit.path_utils import has_moniker, normalize_path, makedir, expend_and_validate_dir, \
    open_file_handle_too_many, wrap_incremental_progress
from .ml_base_object_store import _MlBaseObjectStore, _MlBaseObjectStore_AsyncExecute


class DiskObjectStore(_MlBaseObjectStore, _MlBaseObjectStore_AsyncExecute):
    COPY_BUFFER_SIZE = 1024 * 1024

    def __init__(self, volume_id, path, is_embedded, storage_volume_id=None):
        normalized_path = normalize_path(path)
        self.__path = expend_and_validate_dir(normalized_path, validate_path=False)
        self.__volume_id = volume_id
        self.__is_embedded = is_embedded
        self.__storage_volume_id = storage_volume_id or volume_id
        super(DiskObjectStore, self).__init__()

    @classmethod
    def _get_file_data(cls, full_object_path, target_fileobj=None, progress_callback=None):
        with closing(open_file_handle_too_many(full_object_path)) as src_file:
            actual_target_fileobj = target_fileobj

            if actual_target_fileobj is None:
                actual_target_fileobj = six.BytesIO()

            actual_progress_callback = wrap_incremental_progress(progress_callback)

            buffer_size = 1024 * 1024  # 1MB

            for chunk in iter(lambda: src_file.read(buffer_size), b''):
                actual_target_fileobj.write(chunk)
                actual_progress_callback(len(chunk))

            if target_fileobj is None:
                return actual_target_fileobj.getvalue()

    def get_source_path(self, metadata):
        sha = metadata['@id']

        if self.__is_embedded:
            object_path = os.path.join(self.__path, str(self.__storage_volume_id), self._get_shafile_path(sha))
        else:
            object_path = os.path.join(self.__path, metadata['@path'])

        return object_path

    def _get_loose_object(self, metadata, target_fileobj=None, progress_callback=None):
        logging.debug('get object %s', metadata)

        sha = metadata['@id']

        object_path = self.get_source_path(metadata)

        try:
            data = self._get_file_data(object_path, target_fileobj=target_fileobj, progress_callback=progress_callback)
        except IOError as ex:
            if ex.errno == errno.ENOENT:
                six.raise_from(NonRetryException(str(ex)), None)

            raise

        if target_fileobj is not None:
            return

        blob = Blob()
        blob.set_raw_chunks([data], sha)
        return blob

    @classmethod
    def _get_shafile_path(cls, sha):
        # Check from object dir
        return hex_to_filename('objects', sha)

    def _gen_upload_sync_args(self, obj, progress_callback=None):
        object_name = self._get_shafile_path(obj.sha)

        object_name = os.path.join(self.__path, str(self.__storage_volume_id), object_name)

        return obj.full_path, object_name, progress_callback

    @classmethod
    def __copy_file_from_cloud(cls, src, dest, progress_callback):
        from missinglink.legit.gcs_utils import _handle_file_object_context_write
        from ..gcs_utils import Downloader

        with _handle_file_object_context_write(dest) as fdst:
            Downloader.download_bucket(None, src, target_fileobj=fdst, progress_callback=progress_callback)

    @classmethod
    def __copy_file_from_local(cls, src, dest, progress_callback):
        from shutil import copyfileobj
        from missinglink.legit.gcs_utils import _WriteWrapperStream, _handle_file_object_context_read, _handle_file_object_context_write

        with _handle_file_object_context_read(src) as fsrc:
            with _handle_file_object_context_write(dest) as fdst:
                wrap_fdst = _WriteWrapperStream(fdst, progress_callback)
                copyfileobj(fsrc, wrap_fdst, cls.COPY_BUFFER_SIZE)

    @classmethod
    def _copy_file(cls, src, dest, progress_callback):
        if isinstance(dest, six.string_types):
            makedir(dest)

        if isinstance(src, six.string_types) and has_moniker(src):
            cls.__copy_file_from_cloud(src, dest, progress_callback)
            return

        cls.__copy_file_from_local(src, dest, progress_callback)

    def add_objects_async(self, objects, callback=None, progress_callback=None):
        self._add_objects_async_with_method(objects, self._copy_file, callback, progress_callback=progress_callback)

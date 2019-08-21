# -*- coding: utf-8 -*-
import abc
import contextlib
import os
import logging
import random
import stat
from sqlite3 import OperationalError

import retrying
import six
from lockfile import UnlockError
from lockfile.mkdirlockfile import MkdirLockFile, LockTimeout
from missinglink.core.config import default_missing_link_cache_folder

from .diskcache import Disk
from .diskcache.core import DBNAME
from .ml_disk_cache import MLDiskCache


class RawDisk(Disk):
    def __init__(self, directory, **kwargs):
        if 'save_meta' in kwargs:
            del kwargs['save_meta']  # workaround for old code

        directory = os.path.abspath(directory)
        super(RawDisk, self).__init__(directory, **kwargs)

    def put(self, metadata):
        key = metadata['@id']
        return super(RawDisk, self).put(key)

    def get(self, metadata, raw):
        return super(RawDisk, self).get(metadata, raw)

    def store(self, value, read, key=None):
        return super(RawDisk, self).store(value, read, key)

    def filename(self, metadata=None, value=None):
        # pylint: disable=unused-argument
        hex_name = metadata['@id']

        _, file_extension = os.path.splitext(metadata['@path'])

        sub_dir = os.path.join(hex_name[:2], hex_name[2:4])
        name = hex_name[4:] + file_extension

        filename = os.path.join(sub_dir, name)
        full_path = os.path.join(self._directory, filename)

        return filename, full_path

    def fetch(self, mode, filename, value, read):
        return super(RawDisk, self).fetch(mode, filename, value, read)


def should_retry_init(exception):
    return isinstance(exception, OperationalError)


@six.add_metaclass(abc.ABCMeta)
class BaseFolderStorage(object):
    def __init__(self, cache_directory):
        self.__cache_directory = cache_directory

    @abc.abstractmethod
    def _get_disk(self):
        """
        returns the actual disk storage
        :return: Disk
        """

    @property
    def cache_directory(self):
        # noinspection PyUnresolvedReferences
        return self.__cache_directory

    @staticmethod
    def _is_file_and_size_match(path, size):
        try:
            st = os.stat(path)
        except OSError:
            return False

        if st.st_size != size:
            return False

        return stat.S_ISREG(st.st_mode)

    def has_item(self, metadata):
        if metadata is None:
            return True

        rel_path, full_path = self._get_metadata_cache_paths(metadata)
        return self._is_file_and_size_match(full_path, metadata['@size'])

    def _get_metadata_cache_paths(self, metadata):
        return self._get_disk().filename(metadata)

    def filename(self, metadata):
        _rel_path, full_path = self._get_metadata_cache_paths(metadata)
        return full_path


class FolderStorage(BaseFolderStorage):
    def __init__(self, cache_directory):
        super(FolderStorage, self).__init__(cache_directory)
        self.__disk = RawDisk(cache_directory)

    def _get_disk(self):
        return self.__disk

    def add_item(self, metadata, data):
        with self.add_item_scope(metadata) as fileobj:
            fileobj.write(data)

    @contextlib.contextmanager
    def add_item_scope(self, metadata):
        from missinglink.core.utils.os_utils import safe_make_dirs
        from .diskcache.atomicwrites import atomic_write

        rel_path, full_filename = self._get_metadata_cache_paths(metadata)
        safe_make_dirs(os.path.dirname(full_filename))

        with atomic_write(full_filename, mode='wb') as writer:
            yield writer


class CacheStorage(BaseFolderStorage):
    DEFAULT_CACHE_LIMIT = 2 ** 37  # 128 GB

    def __init__(self, cache_directory, cache_limit=None):
        super(CacheStorage, self).__init__(cache_directory)

        custom_settings = {
            'size_limit': cache_limit or self.DEFAULT_CACHE_LIMIT,
            'eviction_policy': 'least-recently-used',
        }

        self.__cache = self._init_cache(custom_settings)

    def _init_cache(self, custom_settings):
        MLDiskCache.assure_folder(self.cache_directory)

        # were using MkdirLockFile instead of LockFile in order to support storage types where link is not supported
        lock_file = MkdirLockFile(self._get_lock_file_path(self.cache_directory))

        logging.debug('Obtaining CacheStorage lock')
        timeout = self._get_lock_timeout()

        try:
            lock_file.acquire(timeout=timeout)
        except LockTimeout:
            logging.warning('CacheStorage lock not acquired on time; will continue as usual')

        cache_object = self.__init_cache_object(custom_settings)

        self._release_lock(lock_file)

        return cache_object

    @staticmethod
    def _get_lock_file_path(cache_directory):
        return os.path.join(cache_directory, DBNAME)

    @staticmethod
    def _get_lock_timeout():
        min_time = 2 * 60  # 2 minutes
        max_time = 4 * 60  # 4 minutes
        return random.randrange(min_time, max_time)

    @staticmethod
    def _release_lock(lock_file):
        try:
            lock_file.release()
        except UnlockError as exc:
            logging.warning('CacheStorage lock release failed with exception: %s', exc)

    @retrying.retry(stop_max_delay=10000, wait_random_min=200, wait_random_max=1000,
                    retry_on_exception=should_retry_init)
    def __init_cache_object(self, custom_settings):
        return MLDiskCache(self.cache_directory, disk_min_file_size=0, disk=RawDisk, **custom_settings)

    @property
    def cache_limit(self):
        # noinspection PyUnresolvedReferences
        return self.__cache.size_limit

    def _get_disk(self):
        return self.__cache.disk

    def close(self):
        self.__cache.close()

    # noinspection PyUnusedLocal
    @classmethod
    def init_from_config(cls, cache_directory, cache_limit=None, **kwargs):
        return cls(cache_directory=cache_directory, cache_limit=cache_limit, **kwargs)

    def has_item(self, metadata):
        if metadata is None:
            return True

        exists = super(CacheStorage, self).has_item(metadata)

        if exists:
            rel_path, full_path = self._get_metadata_cache_paths(metadata)

            self.__cache.mark_path_accessed_time(rel_path)

        return exists

    def add_item(self, metadata, data):
        from missinglink.legit.path_utils import safe_make_dirs

        full_path = self.filename(metadata)

        dir_name = os.path.dirname(full_path)

        safe_make_dirs(dir_name)

        self.__cache[metadata] = data

    @property
    def storage_params(self):
        return {
            'cache_directory': self.cache_directory,
            'cache_limit': self.cache_limit,
        }


def create_default_storage(cache_folder, cache_limit):
    use_folder_storage = os.environ.get('ML_CACHE_USE_FOLDER_STORAGE') == '1'

    actual_cache_folder = cache_folder or os.environ.get('ML_CACHE_FOLDER', default_missing_link_cache_folder())

    if use_folder_storage:
        return FolderStorage(actual_cache_folder)

    return CacheStorage(actual_cache_folder, cache_limit)

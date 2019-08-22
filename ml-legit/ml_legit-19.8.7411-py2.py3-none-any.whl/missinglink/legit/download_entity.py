# -*- coding: utf-8 -*-
import json
import requests
import importlib
from missinglink.core.config import Config
import logging

from missinglink.core.context import create_empty_context, build_context_from_config
from .local_data_mapping import local_data_mapping

logger = logging.getLogger(__name__)


class DownloadEntity(object):
    __local_data_mapping = local_data_mapping()

    @classmethod
    def __object_from_data(cls, data, creator):
        data_key = json.dumps(data, sort_keys=True)

        data_key += creator.__name__

        return cls.__local_data_mapping(data_key, lambda _: creator(data))

    @classmethod
    def _import_storage(cls, storage_class):
        module_name, class_name = storage_class.rsplit('.', 1)
        m = importlib.import_module(module_name)
        return getattr(m, class_name)

    @classmethod
    def _get_storage(cls, current_data):
        current_data_clone = dict(current_data)
        storage_class = current_data_clone.pop('class')
        return cls._import_storage(storage_class).init_from_config(**current_data_clone)

    @classmethod
    def _get_config(cls, current_data):
        return Config(**current_data)

    @classmethod
    def _get_item_data(cls, repo, metadata, target_fileobj=None, progress_callback=None):
        _, data = repo.object_store.get_raw(metadata, target_fileobj=target_fileobj, progress_callback=progress_callback)

        return data

    @classmethod
    def __download(cls, ctx, storage, data_volume_config, metadata, progress_callback=None):
        from .data_volume import with_repo_dynamic

        with with_repo_dynamic(ctx, data_volume_config, read_only=True) as repo:
            if hasattr(storage, 'add_item_scope'):
                with storage.add_item_scope(metadata) as target_fileobj:
                    cls._get_item_data(repo, metadata, target_fileobj, progress_callback)
            else:
                data = cls._get_item_data(repo, metadata)
                if data is not None:
                    storage.add_item(metadata, data)
                    cls.__notify_all_file_ready(metadata, progress_callback)

    @classmethod
    def __notify_all_file_ready(cls, metadata, progress_callback):
        from .object_store.ml_base_object_store import ProgressCallback

        actual_callback = ProgressCallback.create(progress_callback)

        if actual_callback is not None:
            item_size = metadata['@size']
            actual_callback(item_size, item_size)

    @classmethod
    def download(cls, config, storage, data_volume_config, metadata, headers, progress_callback=None):
        if storage.has_item(metadata):
            cls.__notify_all_file_ready(metadata, progress_callback)
            return

        session = requests.session()
        session.headers.update(headers)

        ctx = create_empty_context()
        build_context_from_config(ctx, session, config)

        cls.__download(ctx, storage, data_volume_config, metadata, progress_callback)

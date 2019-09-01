# -*- coding: utf-8 -*-
import abc
import collections
import six
from ..dulwich.object_store import BaseObjectStore


class ProgressCallback(object):
    _Progress = collections.namedtuple('Progress', 'current total so_far')

    @classmethod
    def create(cls, progress_callback):
        state_progress = dict(so_far=0)

        def progress_callback_wrap(so_far, total, *args, **kwargs):
            if progress_callback is not None:
                progress = cls._Progress(total=total, current=so_far - state_progress['so_far'], so_far=so_far)
                state_progress['so_far'] = so_far
                progress_callback(progress, *args, **kwargs)

        return progress_callback_wrap if progress_callback is not None else None


@six.add_metaclass(abc.ABCMeta)
class _MlBaseObjectStore(BaseObjectStore):
    def __init__(self):
        self._multi_process_control = None

    @staticmethod
    def _create_progress_callback_with_args(progress_callback, *args):
        def wrap(*inner_args, **inner_kwargs):
            if progress_callback:
                progress_callback(*(inner_args + args), **inner_kwargs)

        return wrap

    @classmethod
    def _create_progress_callback(cls, progress_callback):
        return ProgressCallback.create(progress_callback)

    @abc.abstractmethod
    def _get_loose_object(self, metadata, target_fileobj=None, progress_callback=None):
        """

        :param metadata:
        :param target_fileobj:
        :return:
        """

    def get_source_path(self, metadata):
        """

        :param metadata:
        :return:
        """

    def set_multi_process_control(self, multi_process_control):
        self._multi_process_control = multi_process_control

    def get_raw(self, metadata, target_fileobj=None, progress_callback=None):
        """Obtain the raw text for an object.

        :param metadata: metadata for the object.
        :param target_fileobj:
        :param progress_callback:
        :return: tuple with numeric type and object contents.
        """
        from missinglink.legit.dulwich.objects import Blob

        ret = self._get_loose_object(metadata, target_fileobj=target_fileobj, progress_callback=self._create_progress_callback(progress_callback))

        if target_fileobj is not None:
            return Blob.type_num, None

        if ret is not None:
            return ret.type_num, ret.as_raw_string()

        raise KeyError(metadata)


@six.add_metaclass(abc.ABCMeta)
class _MlBaseObjectStore_AsyncExecute(BaseObjectStore):
    @abc.abstractmethod
    def _gen_upload_sync_args(self, obj, progress_callback=None):
        """
        return poaramters to preform the upload
        :param obj:
        :return:
        """

    def _async_execute(self, sync_method, obj, callback=None, progress_callback=None):
        args = self._gen_upload_sync_args(obj, progress_callback=progress_callback)

        def on_finish(result):
            callback(obj)

        self._multi_process_control.execute(sync_method, args=args, callback=on_finish if callback else None)

    @staticmethod
    def _noop(*args, **kwargs):
        pass

    def _add_objects_async_with_method(self, objects, method, callback, progress_callback=None):
        for obj in objects:
            actual_progress_callback = self._create_progress_callback(progress_callback)
            actual_progress_callback_with_obj = self._create_progress_callback_with_args(actual_progress_callback, obj)
            if obj.skip_upload:
                self._async_execute(self._noop, obj, callback=callback, progress_callback=actual_progress_callback_with_obj)
                continue

            self._async_execute(method, obj, callback=callback, progress_callback=actual_progress_callback_with_obj)

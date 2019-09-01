# -*- coding: utf-8 -*-
import contextlib
import csv
import stat
import json

import msgpack
from missinglink.core.exceptions import NonRetryException, MissingLinkException
import logging
import time

from concurrent.futures import ThreadPoolExecutor
from missinglink.core.avro_utils import AvroWriter
from .progress_bar import create_progress_bar
from .download_entity import DownloadEntity
from .metadata_files import MetadataFiles

import tempfile
from contextlib import closing
import sys
import os
from uuid import uuid4
import datetime
from missinglink.core.api import ApiCaller, default_api_retry
from missinglink.core.json_utils import normalize_item
from missinglink.core.multi_process_control import get_multi_process_control
from .path_utils import get_batch_of_files_from_paths, safe_make_dirs, DestPathEnum, enumerate_paths_with_info, \
    get_full_path_using_moniker, expend_and_validate_dir, get_moniker, remove_moniker, is_subdir, \
    open_file_handle_too_many
from missinglink.core.print_status import PrintStatus
from missinglink.core.eprint import eprint
from enum import Enum


class InvalidJsonFile(Exception):
    def __init__(self, filename, ex):
        self.filename = filename
        self.ex = ex

    def __str__(self):
        return '<%s(%r)> (%s)' % (self.__class__.__name__, self.filename, self.ex)


class InvalidDataPath(Exception):
    pass


class InvalidMetadataException(Exception):
    def __init__(self, errors):
        self.errors = errors


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def status_with_timing(message, callback, fp=None, on_summery_data=None):
    fp = fp or sys.stderr

    start_time = datetime.datetime.utcnow()
    status_line = PrintStatus(fp=fp)
    with closing(status_line):
        status_line.print_status(message)

        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(callback)

            while future.running():
                total_time = chop_microseconds(datetime.datetime.utcnow() - start_time)
                status_line.print_status("%s %s" % (message, total_time))

                time.sleep(0.1)

            result = future.result()
            total_time = chop_microseconds(datetime.datetime.utcnow() - start_time)

            if on_summery_data is not None:
                summery_data = on_summery_data(result)
                summery_data = '%s, %s' % (total_time, summery_data)
            else:
                summery_data = str(total_time)

            status_line.print_status('%s Done (%s)' % (message, summery_data))

    return result


class DiskStorage(object):
    def __init__(self, dest_pattern, save_meta):
        self.__dest_pattern = dest_pattern
        self.__save_meta = save_meta

    def close(self):
        pass

    @classmethod
    def _atomic_rename_tmp(cls, full_file_name):
        full_json_filename_tmp = cls._make_tmp_filename(full_file_name)

        try:
            os.rename(full_json_filename_tmp, full_file_name)
        except OSError:
            pass

    @classmethod
    def _make_tmp_filename(cls, full_json_filename):
        return full_json_filename + '.tmp'

    def add_item(self, metadata, data):
        with self.add_item_scope(metadata) as fileobj:
            fileobj.write(data)

    def __add_item_scope_save_meta(self, metadata):
        if not self.__save_meta:
            return

        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)

        full_json_filename = full_filename + '.metadata.json'

        item_meta = {key: val for key, val in metadata.items() if not key.startswith('@')}

        if item_meta:
            with closing(open_file_handle_too_many(self._make_tmp_filename(full_json_filename), 'wt')) as f:
                json.dump(item_meta, f)

            self._atomic_rename_tmp(full_json_filename)

    @contextlib.contextmanager
    def add_item_scope(self, metadata):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        safe_make_dirs(os.path.dirname(full_filename))

        self.__add_item_scope_save_meta(metadata)

        tmp_filename = self._make_tmp_filename(full_filename)

        with closing(open_file_handle_too_many(tmp_filename, 'wb')) as f:
            yield f

        self._set_file_stat(tmp_filename, metadata)
        self._atomic_rename_tmp(full_filename)

    @classmethod
    def _set_file_stat(cls, full_filename, metadata):
        mtime = metadata.get('@mtime')
        if mtime:
            access_time = mtime
            modification_time = mtime
            try:
                if os.path.exists(full_filename):
                    os.utime(full_filename, (access_time, modification_time))
            except OSError as error:
                logging.warning('File - {filename} was cloned twice to the same path.'.format(filename=full_filename))
                logging.warning(error)
                pass

    @staticmethod
    def _is_file_and_size_match(path, size):
        """Test whether a path is a regular file"""
        try:
            st = os.stat(path)
        except OSError:
            return False

        if st.st_size != size:
            return False

        return stat.S_ISREG(st.st_mode)

    def has_item(self, metadata):
        full_filename = DestPathEnum.get_full_path(self.__dest_pattern, metadata)
        return self._is_file_and_size_match(full_filename, metadata['@size'])


class _MissingLinkKeyboardInterrupt(NonRetryException):
    pass


def _wrap_keyboard_interrupt(method):
    def wrap(*args, **kwargs):
        try:
            method(*args, **kwargs)
        except KeyboardInterrupt:
            raise _MissingLinkKeyboardInterrupt()

    return wrap


def _wrap_keyboard_interrupt2(method, *args, **kwargs):
    try:
        method(*args, **kwargs)
    except KeyboardInterrupt:
        raise _MissingLinkKeyboardInterrupt()


class DataSync(object):
    _OP_CODE_MOVE = 'm'
    _OP_CODE_INSERT = 'i'

    def __init__(self, obj_or_ctx, repo, no_progressbar=False, processes=None):
        self.__obj = self.__get_obj(obj_or_ctx)

        self.__repo = repo
        self.__no_progressbar = no_progressbar
        self.__multi_process_control = None

        data_volume_config = self.__repo.data_volume_config

        self.__processes = processes or data_volume_config.object_store_config.get('processes') or -1

        self.__existing_metadata_fields = None

    @classmethod
    def __get_obj(cls, obj_or_ctx):
        return (obj_or_ctx.obj if hasattr(obj_or_ctx, 'obj') else obj_or_ctx) or obj_or_ctx

    @property
    def _session(self):
        return self.__obj.session

    @property
    def _config(self):
        return self.__obj.config

    def get_multi_process_control(self, use_threads=None):
        self.__init_multi_process_if_needed(use_threads)
        return self.__multi_process_control

    def __init_multi_process_if_needed(self, use_threads=None):
        if self.__multi_process_control is None:
            self.__multi_process_control = get_multi_process_control(self.__processes, use_threads=use_threads)
            self.__repo.set_multi_process_control(self.__multi_process_control)

    def close(self):
        logging.debug('%s closing', self.__class__)
        if self.__multi_process_control is not None:
            self.__multi_process_control.close()

        logging.debug('%s closed', self.__class__)

    @property
    def repo(self):
        return self.__repo

    def _upload_file_for_processing(self, file_obj, file_description, file_type=None):
        volume_id = self.__repo.data_volume_config.volume_id

        file_type = file_type or 'json'
        data_object_name = '%s/temp/%s_%s.%s' % (volume_id, file_description, uuid4().hex, file_type)

        content_typse = {
            'json': 'application/json'
        }

        default_mime_type = 'application/octet-stream'
        headers = {'Content-Type': content_typse.get(file_type, default_mime_type)}

        put_url = self._get_temp_secure_url(volume_id, data_object_name, headers)

        self._upload_file(file_obj, put_url, file_description, headers)

        return data_object_name

    @classmethod
    def __filter_op_codes(cls, change_set, op_codes):
        for data in change_set:
            op = data['op']
            if op not in op_codes:
                continue

            yield data

    @classmethod
    def __get_file_to_upload(cls, get_changeset_callable):
        change_set = status_with_timing('Server process index', get_changeset_callable)

        files_to_upload = tempfile.TemporaryFile('w+')

        out_data = csv.writer(files_to_upload)
        total_files_to_upload_or_move = 0
        total_size_to_upload = 0

        # noinspection PyTypeChecker
        for data in cls.__filter_op_codes(change_set, (cls._OP_CODE_MOVE, cls._OP_CODE_INSERT)):
            op = data['op']

            size = int(data['size'])

            needs_upload = 1 if op == cls._OP_CODE_INSERT else None

            if needs_upload:
                total_size_to_upload += size

            total_files_to_upload_or_move += 1

            params = [data['name'], data['size'], data['sha'], data['mtime'], data['ctime'], needs_upload]

            out_data.writerow(params)

        files_to_upload.seek(0)

        return files_to_upload, total_files_to_upload_or_move, total_size_to_upload

    def _process_index(self, data_path, object_name, isolation_token):
        index = self.__repo.open_index()

        def get_changeset():
            return index.get_changeset('gs://' + object_name, isolation_token)

        files_to_upload, total_files_to_upload_or_move, total_size_to_upload = self.__get_file_to_upload(get_changeset)

        def iter_files():
            files_to_upload.seek(0)
            reader = csv.reader(files_to_upload)

            for row in reader:
                if not row:
                    continue

                current_name_rel, current_size, current_sha, current_mtime, current_ctime, needs_upload = row

                path = get_full_path_using_moniker(data_path, current_name_rel)

                yield {
                    'path': path,
                    'name': current_name_rel,
                    'size': int(current_size),
                    'sha': current_sha,
                    'mtime': float(current_mtime),
                    'ctime': float(current_ctime),
                    'needs_upload': needs_upload
                }

        return iter_files(), total_files_to_upload_or_move, total_size_to_upload

    def __prepare_index_file(self, index_entities_file, file_type):
        return self._upload_file_for_processing(index_entities_file, 'Index', file_type=file_type)

    def _upload_full_index(self, index_entities_file, isolation_token, file_type=None):
        object_name = self.__prepare_index_file(index_entities_file, file_type=file_type)

        index = self.__repo.open_index()

        def set_entries_operation():
            return index.set_entries_from_url('gs://' + object_name, isolation_token)

        return status_with_timing('Server process index', set_entries_operation)

    def _get_files_to_upload_from_file(self, data_path, index_entities_file_obj, isolation_token, file_type=None):
        object_name = self.__prepare_index_file(index_entities_file_obj, file_type=file_type)

        return self._process_index(data_path, object_name, isolation_token)

    def upload_and_update_metadata(self, avro_metadata_file_obj, isolation_token=None, file_type=None):
        object_name = self._upload_file_for_processing(avro_metadata_file_obj, 'Metadata', file_type=file_type)

        def add_data():
            return self.__repo.metadata.add_data_using_url('gs://' + object_name, isolation_token)

        status_with_timing('Server process metadata', add_data)

    class EntryType(Enum):
        File = 1
        Metadata = 2

    @classmethod
    def __enum_meta(cls, data_path, rel_file_name):
        def gen():
            for rel_path_key, current_data in MetadataFiles.get_metadata(data_path, rel_file_name):
                yield cls.EntryType.Metadata, rel_path_key, current_data

        return gen

    @classmethod
    def __enum_files(cls, rel_file_name, file_info):
        def gen():
            yield cls.EntryType.File, rel_file_name, file_info

        return gen

    @classmethod
    def __status_line_for_sync(cls, status_line, skip_metadata):
        import humanize

        def print_status(total_files, total_files_size, total_metadata):
            metadata_info = 'metadata skipped' if skip_metadata else 'metadata found: {:,}'.format(total_metadata)

            status_line.print_status(
                'Total files {:,} ({}) ({})', total_files,
                humanize.naturalsize(total_files_size), metadata_info)

        return print_status

    @classmethod
    def __enum_create_combined_index_and_metadata(cls, full_data_path, full_data_path_root, skip_metadata):
        total_files = 0
        total_files_size = 0
        total_metadata = 0

        for file_info in enumerate_paths_with_info(full_data_path, root_path=full_data_path_root):
            rel_file_name = file_info['rel_file_name']

            if not rel_file_name.endswith(MetadataFiles.metadata_ext):
                total_files += 1
                total_files_size += file_info['size']
                enum_files_types = cls.__enum_files(rel_file_name, file_info)
            elif not skip_metadata:
                total_metadata += 1
                enum_files_types = cls.__enum_meta(full_data_path_root, rel_file_name)
            else:
                continue  # pragma: no cover

            yield enum_files_types, total_files, total_files_size, total_metadata

    @classmethod
    def __create_combined_index_and_metadata(cls, full_data_path, status_line, full_data_path_root=None, skip_metadata=False):
        print_status = cls.__status_line_for_sync(status_line, skip_metadata)

        for enum_files_types, total_files, total_files_size, total_metadata in cls.__enum_create_combined_index_and_metadata(full_data_path, full_data_path_root, skip_metadata):
            for file_type, rel_key, data in enum_files_types():
                yield file_type, rel_key, data

            print_status(total_files, total_files_size, total_metadata)

    def upload_in_batches(self, files_info, total_files=None, callback=None, isolation_token=None, progress_callback=None):
        use_threads = None

        if not self.__repo.direct_bucket_upload:
            # in no direct bucket upload we upload to our bucket thru secure urls
            # the process of getting secure urls will lock the processes of multiprocess (I don't know why)
            # As a fallback we use the threaded upload
            use_threads = True

        multi_process_control = self.get_multi_process_control(use_threads)
        try:
            total_files = total_files or len(files_info)
            batch_size = max(min(total_files // 100, 250), 250)  # FIXME: hardcoded

            for files_info_batch in get_batch_of_files_from_paths(files_info, batch_size, total_files=total_files):
                self.__repo.stage(
                    files_info_batch,
                    callback=callback,
                    isolation_token=isolation_token,
                    progress_callback=progress_callback,
                    is_embedded_mode=self.__is_embedded_mode
                )

            multi_process_control.join()
        except Exception as ex:
            if not isinstance(ex, MissingLinkException):
                logging.exception('execute failed')

            multi_process_control.terminate()
            raise

    @classmethod
    def __join_download_all(cls, multi_process_control):
        try:
            multi_process_control.join()
        except Exception as ex:
            multi_process_control.terminate()

            if isinstance(ex, _MissingLinkKeyboardInterrupt):
                raise KeyboardInterrupt()

            raise

    def download_all(self, query, _remove_me, dest_pattern, batch_size, processes, **kwargs):
        root_folder = DestPathEnum.find_root(dest_pattern)

        save_meta = kwargs.pop('save_meta', True)
        isolation_token = kwargs.pop('isolation_token', None)
        use_threads = kwargs.pop('use_threads', None)

        def create_progress_callback(progress_bar):
            def handle_progress(item, progress):
                progress_bar.update(progress.current)

            return handle_progress

        def create_callback(progress_bar, total_files):
            ctx = {'total_downloaded': 0}

            def handle_item(item):
                import humanize

                file_name = DestPathEnum.get_full_path(dest_pattern, item)
                rel_path = os.path.relpath(file_name, root_folder)
                phase = item.get('phase', 'all')
                phase_meta.setdefault(phase, {})[rel_path] = item

                ctx['total_downloaded'] += 1
                progress_bar.set_postfix_str('%s/%s' % (humanize.intcomma(ctx['total_downloaded']), humanize.intcomma(total_files)))

            return handle_item

        multi_process_control = get_multi_process_control(processes, use_threads=use_threads)
        download_iter = self.create_download_iter(query, batch_size, isolation_token=isolation_token)

        phase_meta = {}

        storage = DiskStorage(dest_pattern, save_meta)

        total_data_points_size = download_iter.total_data_points_size
        with create_progress_bar(total=total_data_points_size, desc="Downloading", unit='B', unit_scale=True, ncols=80, disable=self.__no_progressbar) as bar:
            item_callback = create_callback(bar, download_iter.total_data_points)
            progress_callback = create_progress_callback(bar)
            try:
                for normalized_item in download_iter.fetch_all():
                    self.__async_download_normalized_item(multi_process_control, storage, normalized_item, item_callback, progress_callback)
            finally:
                self.__join_download_all(multi_process_control)

            return phase_meta

    def __async_download_normalized_item(self, process_control, storage, normalized_item, callback=None, progress_callback=None):
        def wrap_callback_func(current_item):
            def wrapper(_):
                callback(current_item)

            return wrapper

        def wrap_progress_callback_func(current_item):
            def wrapper(*args, **kwargs):
                progress_callback(current_item, *args, **kwargs)

            return wrapper

        logging.debug('prepare for download %s', normalized_item)

        actual_progress_callback = wrap_progress_callback_func(normalized_item) if progress_callback is not None else None
        actual_callback = wrap_callback_func(normalized_item) if callback is not None else None

        return process_control.execute(
            _wrap_keyboard_interrupt2,
            args=(DownloadEntity.download, ) + (self._config, storage, self.repo.data_volume_config, normalized_item, self._session.headers, actual_progress_callback),
            callback=actual_callback)

    class DownloadIterResults(object):
        max_server_results = 1000  # TODO: server should return EOF oin last packet

        def __init__(self, repo, query, batch_size, silent=False, isolation_token=None):
            from .metadata_db.limit_visitor import LimitVisitor
            from .scam import QueryParser, visit_query

            self.__query = query
            self.__repo = repo
            self.__query_offset = 0
            self.__total_data_points = None
            self.__total_data_points_size = None
            self.__current_iter = None
            self.__is_async = batch_size == -1
            self.__silent = silent
            self.__batch_size = batch_size
            self.__isolation_token = isolation_token

            if (self.__batch_size or 0) < 0:
                self.__batch_size = None

            if self.__query:
                tree = QueryParser().parse_query(self.__query)

                self.__limit_visitor = LimitVisitor()
                visit_query(self.__limit_visitor, tree)
            else:
                self.__limit_visitor = None

        def __get_next_results(self):
            def do_query():
                query_offset = None if not self.__query_offset else self.__query_offset
                return self.__repo.metadata.query(self.__query, is_async=self.__is_async, start_index=query_offset, isolation_token=self.__isolation_token, return_schema=True)

            if not self.__silent:
                def on_summery_data(results):
                    import humanize
                    _, query_current_total_data_points, query_total_size = results

                    return '%s, %s Rows' % (humanize.naturalsize(query_total_size), humanize.intcomma(query_current_total_data_points))

                current_results, current_total_data_points, total_size = status_with_timing('Execute Query', do_query, on_summery_data=on_summery_data)
            else:
                current_results, current_total_data_points, total_size = do_query()

            def iter_items():
                next_results = current_results
                has_limit = self.__limit_visitor and self.__limit_visitor.limit
                while True:
                    has_items = False
                    items_in_this_batch = 0
                    for metadata in next_results:
                        self.__query_offset += 1
                        items_in_this_batch += 1
                        has_items = True
                        yield normalize_item(metadata)

                    if self.__is_async:  # In async query we call all the results in one batch
                        break

                    if not has_items:
                        break

                    if self.max_server_results > items_in_this_batch:
                        break

                    if has_limit and self.__query_offset >= self.__limit_visitor.limit:
                        break

                    next_results, _, _ = do_query()

            return iter_items(), current_total_data_points, total_size

        @property
        def total_data_points_size(self):
            self.__prepare_iter_if_needed()

            return self.__total_data_points_size

        @property
        def total_data_points(self):
            self.__prepare_iter_if_needed()

            return self.__total_data_points

        def __prepare_iter_if_needed(self):
            if self.__current_iter is not None:
                return

            self.__current_iter, self.__total_data_points, self.__total_data_points_size = self.__get_next_results()

        def fetch_all(self):
            self.__prepare_iter_if_needed()

            for item in self.__current_iter:
                yield item

    def create_download_iter(self, query, batch_size=None, silent=False, isolation_token=None):
        return self.DownloadIterResults(self.__repo, query, batch_size, silent, isolation_token)

    def download_items(self, normalized_metadata_items, storage, multi_process_control):
        futures = []
        for normalized_item in normalized_metadata_items:
            async_result = self.__async_download_normalized_item(multi_process_control, storage, normalized_item)
            futures.append((async_result, normalized_item))

        for async_result, normalized_item in futures:
            async_result.wait()
            async_result.get()

    @classmethod
    def save_metadata(cls, root_dest, metadata):
        for key, val in metadata.items():
            if key is None:
                key = 'unknown'

            json_metadata_file = os.path.join(root_dest, '.{key}.metadata.json'.format(key=key))  # we save as dot file so it will be ignore if you sync the same folder

            with open(json_metadata_file, 'w') as f:
                eprint('saving metadata file %s' % json_metadata_file)
                json.dump(val, f)

    @classmethod
    def __write_avro_index(cls, msg_pack_index_file, index_schema):
        combined_avro_index_files = tempfile.TemporaryFile('wb+')

        with closing(AvroWriter(combined_avro_index_files, key_name='name', schema=index_schema)) as index_avro_writer:
            unpacker = msgpack.Unpacker(msg_pack_index_file, raw=False)

            index_avro_writer.append_data(unpacker)

        return combined_avro_index_files

    @classmethod
    def __write_avro_metadata(cls, msg_pack_metadata_file, metadata_schema):
        combined_avro_meta_files = tempfile.TemporaryFile('wb+')

        with closing(AvroWriter(combined_avro_meta_files, schema=metadata_schema)) as metadata_avro_writer:
            unpacker = msgpack.Unpacker(msg_pack_metadata_file, raw=False)
            metadata_avro_writer.append_data(unpacker)

        return combined_avro_meta_files

    def __get_index_and_metadata_info(self, files_info_iter, stop_on_first_error=True, skip_metadata=False):
        from .index_metadata_info_generator import IndexMetadataInfoGenerator

        info_generator = IndexMetadataInfoGenerator(skip_metadata, is_embedded_mode=self.__is_embedded_mode,
                                                    existing_metadata_fields=self.__existing_metadata_fields)
        return info_generator.generate(files_info_iter, stop_on_first_error)

    @property
    def __data_volume_config(self):
        return self.repo.data_volume_config

    @property
    def __is_embedded_mode(self):
        return self.__data_volume_config.embedded

    @property
    def __is_disk_type(self):
        bucket_name = self.__data_volume_config.bucket_name

        return get_moniker(bucket_name) == 'file'

    @classmethod
    def __validate_sub_dir(cls, root, folder):
        if is_subdir(folder, root):
            return

        raise InvalidDataPath('path %s is not inside bucket folder %s' % (folder, root))

    def __validate_data_path(self, data_path, data_path_root):
        full_data_path = expend_and_validate_dir(data_path)

        if self.__data_volume_config.embedded or not self.__is_disk_type:
            full_data_path_root = expend_and_validate_dir(data_path_root) if data_path_root is not None else full_data_path

            self.__validate_sub_dir(full_data_path_root, full_data_path)

            return full_data_path_root, full_data_path

        bucket_name = self.__data_volume_config.bucket_name

        path_name = remove_moniker(bucket_name)

        full_bucket_name = expend_and_validate_dir(path_name)

        self.__validate_sub_dir(full_bucket_name, full_data_path)

        return full_bucket_name, full_data_path

    def __generate_index_and_metadata_info(self, data_path, data_path_root, stop_on_first_error=True, skip_metadata=False):
        full_data_path_root, full_data_path = self.__validate_data_path(data_path, data_path_root)

        status_line = PrintStatus(fp=sys.stderr)

        files_info_iter = self.__create_combined_index_and_metadata(full_data_path, status_line,
                                                                    full_data_path_root=full_data_path_root,
                                                                    skip_metadata=skip_metadata)

        with closing(status_line):
            index_info, metadata_info = self.__get_index_and_metadata_info(files_info_iter, stop_on_first_error,
                                                                           skip_metadata=skip_metadata)

        return index_info, metadata_info

    def upload_index_and_metadata(self, data_path, isolation_token=None, data_path_root=None, skip_metadata=False):
        full_data_path_root, full_data_path = self.__validate_data_path(data_path, data_path_root)

        index_info, metadata_info = self.__generate_index_and_metadata_info(data_path, data_path_root, skip_metadata=skip_metadata)

        msg_pack_metadata_file, metadata_schema, metadata_errors = metadata_info

        if metadata_errors:
            raise InvalidMetadataException(metadata_errors)

        if metadata_schema:
            combined_avro_meta_files = self.__write_avro_metadata(msg_pack_metadata_file, metadata_schema)

            self.upload_and_update_metadata(combined_avro_meta_files, isolation_token, file_type='avro')

        total_files_to_upload = 0
        total_size_to_upload = 0
        files_to_upload_gen = []

        msg_pack_index_file, total_data_files, total_size_data_files, index_schema = index_info

        if total_data_files > 0:
            combined_avro_index_files = self.__write_avro_index(msg_pack_index_file, index_schema)

            if self.repo.data_volume_config.embedded:
                files_to_upload_gen, total_files_to_upload, total_size_to_upload = self._get_files_to_upload_from_file(
                    full_data_path_root, combined_avro_index_files, isolation_token, file_type='avro')
            else:
                self._upload_full_index(combined_avro_index_files, isolation_token, file_type='avro')

        return files_to_upload_gen, (total_data_files, total_size_data_files), (total_files_to_upload, total_size_to_upload)

    def validate_metadata(self, data_path, data_path_root=None, **_):
        self.__validate_data_path(data_path, data_path_root)

        index_info, metadata_info = self.__generate_index_and_metadata_info(data_path, data_path_root,
                                                                            stop_on_first_error=False)
        msg_pack_metadata_file, metadata_schema, metadata_errors = metadata_info

        if metadata_errors:
            raise InvalidMetadataException(metadata_errors)

    def _get_temp_secure_url(self, volume_id, data_object_name, headers):
        logging.debug('temp url for %s', data_object_name)

        url = 'data_volumes/{volume_id}/gcs_urls'.format(volume_id=volume_id)

        msg = {
            'methods': 'PUT',
            'paths': [data_object_name],
            'content_type': headers.get('Content-Type'),
            'temp': True,
        }

        result = ApiCaller.call(self._config, self._session, 'post', url, msg, retry=default_api_retry())

        put_url = result['put'][0]

        return put_url

    def _upload_file(self, file_obj, put_url, file_description, headers=None):
        from .gcs_utils import Uploader

        context = dict(so_far=0)

        def update_bar(so_far, _total=None):
            current = so_far - context['so_far']
            context['so_far'] = so_far
            bar.update(current)

        logging.debug('uploading using %s', put_url)
        with create_progress_bar(
                total=file_obj.tell(), desc="Uploading {}".format(file_description), unit='B', ncols=80,
                disable=self.__no_progressbar, unit_scale=True) as bar:
            Uploader.upload_http(put_url, None, file_obj, headers, progress_callback=update_bar)

    def set_existing_metadata_fields(self, existing_metadata_fields):
        self.__existing_metadata_fields = existing_metadata_fields

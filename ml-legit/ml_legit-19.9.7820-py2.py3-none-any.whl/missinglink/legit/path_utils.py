# -*- coding: utf-8 -*-
import logging
import datetime
import os
import shutil
import errno
import six
from missinglink.core.exceptions import AccessDenied
from missinglink.legit.file_hash_generator import FileHashGenerator

REQUIRED_FILE_INFO_FIELDS = ['path', 'sys', 'size']

epoch = datetime.datetime.utcfromtimestamp(0)


class StorageType(object):
    Local = 'local'
    S3 = 's3'


def wrap_incremental_progress(progress_callback):
    state_progress = dict(so_far=0)

    def progress_callback_wrap(current, total=None):
        if progress_callback is not None:
            state_progress['so_far'] += current
            progress_callback(state_progress['so_far'], total)

    return progress_callback_wrap


def _get_scan_dir():
    try:
        from os import scandir
    except ImportError:
        # noinspection PyUnresolvedReferences
        from scandir import scandir

    return scandir


ignore_files = ['.DS_Store']


class StorageUtils(object):
    @classmethod
    def split_bucket_prefix(cls, bucket_with_path):
        bucket_with_path = remove_moniker(bucket_with_path)

        try:
            bucket, prefix = bucket_with_path.split('/', 1)

            if not prefix.endswith('/'):
                prefix += '/'
        except ValueError:
            bucket, prefix = bucket_with_path, ''

        return bucket, prefix


class LocalEnumerator(object):

    @classmethod
    def _file_to_info(cls, path, st, fields=None):
        params = {
            'path': path,
            'sys': StorageType.Local,
            'mtime': st.st_mtime,
            'ctime': st.st_ctime,
            'size': st.st_size,
            'mode': st.st_mode
        }

        if fields:
            return {key: value for key, value in params.items() if (key in fields or key in REQUIRED_FILE_INFO_FIELDS)}

        return params

    @classmethod
    def _file_name_to_info(cls, filename, fields=None):
        return cls._file_to_info(filename, os.stat(filename), fields)

    @classmethod
    def _file_entry_to_info(cls, entry, fields=None):
        return cls._file_to_info(entry.path, entry.stat(), fields)

    @classmethod
    def _recursive_scan(cls, root_path, current_path, fields, skip_dot_files):
        scandir = _get_scan_dir()

        def rel_path(current_info, current_root_path):
            current_info['rel_file_name'] = os.path.relpath(current_info['path'], current_root_path)
            return current_info

        try:
            for entry in scandir(current_path):
                if skip_dot_files and entry.name.startswith('.'):
                    continue

                # in windows, is_dir() will return False for a symlink
                if _is_dir_or_symlink(entry):
                    for info in cls._recursive_scan(root_path, entry.path, fields, skip_dot_files):
                        yield rel_path(info, root_path)

                    continue

                yield rel_path(cls._file_entry_to_info(entry, fields), root_path)
        except OSError as ex:
            if ex.errno == errno.ENOTDIR:
                yield rel_path(cls._file_name_to_info(current_path, fields), root_path)
                return

            raise

    @classmethod
    def enumerate_path(cls, path, fields=None, root_path=None, skip_dot_files=True):
        def get_root_path():
            if os.path.isdir(path):
                return path

            return os.path.dirname(path)

        root_path = root_path or get_root_path()
        for info in cls._recursive_scan(root_path, path, fields, skip_dot_files=skip_dot_files):
            yield info


class S3Enumerator(LocalEnumerator):
    @classmethod
    def get_bucket_name(cls, path):
        import boto3
        from botocore.exceptions import ClientError

        path = remove_moniker(path)
        bucket_name = path.split('/')[0]

        try:
            client = boto3.client('s3')

            response = client.get_bucket_location(Bucket=bucket_name)

            location = response.get('LocationConstraint') or 'us-east-1'
            return '%s (%s)' % (path, location)
        except ClientError:
            pass

    @classmethod
    def _info_to_file_info(cls, item, fields=None):
        params = {
            'path': item['Key'],
            'rel_file_name': item['Key'],
            'sys': StorageType.S3,
        }

        if fields is None or 'size' in fields:
            params['size'] = item['Size']

        etag = item['ETag'].replace('"', '')

        if fields is None or 'etag' in fields:
            params['etag'] = etag

        if fields is None or 'mtime' in fields:
            last_modified = item['LastModified'].replace(tzinfo=None)
            params['mtime'] = (last_modified - epoch).total_seconds()

        if fields is None or 'sha' in fields:
            params['sha'] = FileHashGenerator.file_etag_to_hash(etag)

        params['url'] = '{moniker}{bucket}/{Key}'.format(**item)

        return params

    @classmethod
    def _create_s3_paginator(cls, **kwargs):
        import boto3

        client = boto3.client('s3')
        paginator = client.get_paginator('list_objects_v2')

        return paginator.paginate(**kwargs)

    @classmethod
    def enumerate_path(cls, path, fields=None, root_path=None, skip_dot_files=True):
        from botocore.exceptions import ClientError

        bucket, prefix = StorageUtils.split_bucket_prefix(path)

        try:
            for page in cls._create_s3_paginator(Bucket=bucket, Prefix=prefix):
                for item in page.get('Contents', []):
                    if item['Key'].endswith('/'):  # skip folders
                        continue

                    item['bucket'] = bucket
                    item['moniker'] = s3_moniker

                    yield cls._info_to_file_info(item, fields)
        except ClientError as ex:
            if ex.response.get('Error', {}).get('Code') == 'AccessDenied':
                raise AccessDenied('Access denied accessing bucket "{}"'.format(bucket))

            raise


def bucket_print_name(path):
    if path.startswith(s3_moniker):
        return S3Enumerator.get_bucket_name(path)

    return path


s3_moniker = 's3://'


def enumerate_path_with_info(path, fields=None, root_path=None, skip_dot_files=True):
    if path.startswith(s3_moniker):
        enumerate_class = S3Enumerator
    else:
        enumerate_class = LocalEnumerator
        root_path = expend_and_validate_dir(root_path)
        path = expend_and_validate_path(path)

    for file_info in enumerate_class.enumerate_path(path, fields, root_path, skip_dot_files=skip_dot_files):
        full_object_name = file_info['path']
        file_name = os.path.basename(full_object_name)

        if file_name in ignore_files:
            continue

        yield file_info


def enumerate_paths_with_info(paths, fields=None, root_path=None, skip_dot_files=True):
    if isinstance(paths, six.string_types):
        paths = [paths]

    for path in paths:
        for file_info in enumerate_path_with_info(path, fields=fields, root_path=root_path, skip_dot_files=skip_dot_files):
            yield file_info


def enumerate_paths(paths):
    for file_info in enumerate_paths_with_info(paths, fields=['size']):
        yield file_info['path']


def is_glob(path):
    return '*' in path or '?' in path


def has_var(path):
    return '$' in path or (path.startswith('{') and path.endswith('}'))


def __validate_path_if_needed(path, validate_path):
    def path_exists():
        # windows symlinks return False for `exists` and True for `lexists`
        return os.path.exists(path) or os.path.lexists(path)

    if not is_glob(path) and validate_path and not path_exists():
        raise IOError('path %s not found' % path)


def __validate_dir_if_needed(path, validate_path):
    if not validate_path:
        return

    if not os.path.isdir(path):
        raise IOError('folder %s not found' % path)


def __unslash(path):
    if path.endswith(os.sep):
        path = os.path.join(path, '')

    return path


def __expend_and_validate_path(path, expand_vars, validate_path, abs_path, validate_nethod):
    if path is None:
        return path

    result_path = path

    if expand_vars:
        result_path = os.path.expandvars(result_path)

    if has_moniker(path):
        return result_path

    result_path = os.path.expanduser(result_path)

    if abs_path:
        result_path = os.path.abspath(result_path)

    validate_nethod(result_path, validate_path)

    result_path = __unslash(result_path)

    return result_path


def expend_and_validate_path(path, expand_vars=True, validate_path=True, abs_path=True):
    return __expend_and_validate_path(path, expand_vars, validate_path, abs_path, __validate_path_if_needed)


def expend_and_validate_dir(path, expand_vars=True, validate_path=True, abs_path=True):
    return __expend_and_validate_path(path, expand_vars, validate_path, abs_path, __validate_dir_if_needed)


def __fill_chunk(l, n):
    result = []

    for _ in range(n):
        try:
            result.append(next(l))
        except StopIteration:
            break

    return result


def chunks(l, n, total=None):
    """Yield successive n-sized chunks from l."""
    if isinstance(l, (list, tuple)):
        it = iter(l)
    else:
        it = l

    for i in range(0, total or len(l), n):
        yield __fill_chunk(it, n)


def get_batch_of_files_from_paths(file_names, batch_size, total_files=None):
    for batch in chunks(file_names, batch_size, total=total_files):
        if not batch:
            return

        yield batch


def safe_make_dirs(dir_name):
    if not dir_name:
        return

    try:
        os.makedirs(dir_name)
    except OSError as ex:
        if ex.errno != errno.EEXIST:
            raise


def path_elements(path):
    if path.endswith(os.sep):
        path = path[:-1]

    folders = []
    while True:
        path, folder = os.path.split(path)

        if len(folder) > 0:
            folders.append(folder)
            continue

        if len(path) > 0:
            folders.append(path)

        break

    folders.reverse()

    return folders


def safe_rm_tree(path):
    try:
        shutil.rmtree(path)
    except OSError as ex:
        if ex.errno != errno.ENOENT:
            raise


class DestPathEnum(object):
    @classmethod
    def find_root(cls, dest):
        elements = path_elements(dest)

        root = []
        for element in elements:
            if has_var(element):
                break

            root.append(element)

        return os.path.join(*root)

    @classmethod
    def _get_path_vars(cls, path):
        actual_path = path or ''
        path_no_ext, file_extension = os.path.splitext(actual_path)

        return {
            'name': os.path.basename(actual_path),
            'dir': os.path.dirname(actual_path),
            'base_name': os.path.basename(path_no_ext),
            'extension': file_extension
        }

    @classmethod
    def ___add_sys_var(cls, name, value, current_vars):
        names = set()
        names.add(name)
        names.add(name.replace('_', '-'))
        names.add(name.replace('_', ''))

        for current_name in names:
            current_vars['@' + current_name] = value

            if current_name not in current_vars:
                current_vars[current_name] = value

    @classmethod
    def __fill_in_vars(cls, path, replace_vars):
        replace_vars_keys = sorted(replace_vars.keys(), reverse=True)

        for var_name in replace_vars_keys:
            var_value = replace_vars[var_name]
            path = path.replace('$' + var_name, str(var_value))
            path = path.replace('#' + var_name, str(var_value))
            path = path.replace('{%s}' % var_name, str(var_value))

        return path

    @classmethod
    def __handle_path(cls, lookup_items, dest):
        if '@path' not in lookup_items:
            return

        path_items = cls._get_path_vars(lookup_items['@path'])

        # in case the user has already specify '.' in the ext don't use dot in the var
        if '.$ext' in dest or '.$@ext' in dest:
            path_items['extension'] = path_items['extension'][1:]

        # support short form as well
        path_items['ext'] = path_items['extension']

        for key, val in path_items.items():
            cls.___add_sys_var(key, val, lookup_items)

    @classmethod
    def get_full_path(cls, dest, item):
        actual_item = item or {}
        lookup_items = dict(actual_item)

        cls.__handle_path(lookup_items, dest)

        cls.___add_sys_var('no_dir', '', lookup_items)

        item_id = lookup_items.get('@id')
        cls.___add_sys_var('id', item_id, lookup_items)

        phase = lookup_items.get('@phase')
        cls.___add_sys_var('phase', phase, lookup_items)
        lookup_items['@'] = phase

        dest_file = cls.__fill_in_vars(dest, lookup_items)

        return dest_file

    @classmethod
    def get_dest_path(cls, dest_folder, dest_file):
        if not dest_file:
            dest_file = '$@name'

        return os.path.join(dest_folder, dest_file)


def is_subdir(path, directory):
    path = os.path.realpath(path)
    directory = os.path.realpath(directory)
    relative = os.path.relpath(path, directory)

    return not relative.startswith(os.pardir + os.sep)


def get_moniker(name, default_moniker=None):
    if name is None:
        return None

    try:
        index = name.index('://')
        return name[:index]
    except ValueError:
        if default_moniker:
            return get_moniker(default_moniker + name)

        return None


def has_moniker(name):
    return '://' in name


def remove_moniker(name):
    try:
        index = name.index('://')
        return name[index + 3:]
    except ValueError:
        return name


def __inc_soft_limit():
    import resource

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    hard = int(os.environ.get('_ML_RLIMIT_NOFILE', 10000)) if hard == resource.RLIM_INFINITY else hard
    total_soft = min(soft * 2, hard)

    logging.info('soft file limit increase %s => %s (%s)', soft, total_soft, hard)
    resource.setrlimit(resource.RLIMIT_NOFILE, (total_soft, hard))


def _open_file(name, mode):
    return open(name, mode)


def open_file_handle_too_many(full_path_to_data, mode='rb'):
    while True:
        try:
            return _open_file(full_path_to_data, mode)
        except (IOError, OSError) as ex:
            if ex.errno == errno.EMFILE:  # too many open files
                __inc_soft_limit()
                continue

            raise


def makedir(file_name):
    try:
        os.makedirs(os.path.dirname(file_name))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def get_full_path_using_moniker(full_path, rel_path_or_full_path):
    if not has_moniker(full_path) or get_moniker(full_path) == 'file':
        return os.path.join(full_path, rel_path_or_full_path)

    bucket, _prefix = StorageUtils.split_bucket_prefix(full_path)

    return '{moniker}://{bucket}/{path}'.format(moniker=get_moniker(full_path), bucket=bucket, path=rel_path_or_full_path)


def normalize_path(path):
    is_windows = os.name == 'nt'
    if not is_windows:
        return path

    if path.startswith('/'):
        root_path = os.path.abspath(os.sep)
        path = os.path.join(root_path, path[1:])

    return path.replace('/', '\\')


def get_path_files(path):
    scandir = _get_scan_dir()

    for entry in scandir(path):
        if _is_dir_or_symlink(entry):
            for file_path in get_path_files(entry.path):
                yield file_path

            continue

        yield entry.path


def _is_dir_or_symlink(entry):
    return entry.is_dir() or entry.is_symlink()

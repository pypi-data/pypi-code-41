from ._dataflowconstants import *
from ._filecache import FileCache
from ._stat import create_stat, stat_to_dict
from ._streamingreader import StreamingReader, UnknownStreamSizeError
from azureml.dataprep import Dataflow, col, get_stream_properties
from azureml.dataprep.api._loggerfactory import _LoggerFactory
from azureml.dataprep.api.engineapi.api import get_engine_api
from azureml.dataprep.api.engineapi.typedefinitions import DownloadStreamInfoMessageArguments
from azureml.dataprep.api.functions import get_portable_path
from azureml.dataprep.native import StreamInfo
from datetime import datetime
from errno import EFBIG, ENOENT
from fuse import FuseOSError, Operations, FUSE
from stat import S_IFREG
import sys
import tempfile
from time import time
from typing import List, Optional


log = _LoggerFactory.get_logger('dprep.fuse')


class MountOptions:
    def __init__(self,
                 data_dir: str = None,
                 max_size: int = None,
                 free_space_required: int = None):
        """
        Configuration options for file mounting.

        .. remarks::

            Depending on the source of the streams mounted, it might be necessary to fully download a file locally
                before it can be opened by the file system. For sources that support streaming, access to the file
                can be provided without this requirement. In both cases, it is possible to configure the system
                to cache the data locally. This can be useful when specific files will be accessed multiple times
                and the source of the data is remote to the current compute. These downloaded and cached files will
                be stored in the system's tmp folder by default, but this can be overriden by manually specifying a
                data_dir.

            The max_size and free_space_required parameters can be used to limit how much data will be downloaded
                or cached locally. If accessing a file requires that it be downloaded, then the least recently used
                files will be deleted after the download completes in order to stay within these parameters. If a file
                that needs to be downloaded before it can be opened by the file system does not fit within the available
                space, an error will be returned.

        :param data_dir: The directory to use to download or cache files locally. If none is provided, the system's
            temp folder is used.
        :param max_size: The maximum amount of memory, in megabytes, that can be stored in data_dir.
        :param free_space_required: How much space should be kept available in the data_dir volume.
        """
        self.data_dir = data_dir
        self.max_size = max_size
        self.free_space_required = free_space_required


class StreamDetails:
    def __init__(self,
                 stream_info: StreamInfo,
                 portable_path: str,
                 size: Optional[int],
                 last_modified: Optional[datetime],
                 can_seek: bool):
        self.stream_info = stream_info
        self.portable_path = portable_path
        self.size = size
        self.last_modified = last_modified
        self.can_seek = can_seek
        self.can_stream = self.size is not None and self.can_seek


class _DPrepFuse(Operations):
    def __init__(self,
                 dataflow: Dataflow,
                 files_column: str,
                 base_path: str = None,
                 mount_options: MountOptions = None):
        if mount_options is None:
            mount_options = MountOptions()

        log.debug('Initializing mount.', extra=dict(max_size=mount_options.max_size,
                                                    free_space_required=mount_options.free_space_required))

        self._engine_api = get_engine_api()
        self._dataflow = dataflow.add_column(get_portable_path(col(files_column), base_path),
                                             PORTABLE_PATH,
                                             files_column)
        self._files_column = files_column
        self._mount_timestamp = int(time())
        mount_options.data_dir = mount_options.data_dir or tempfile.mkdtemp()
        mount_options.max_size = mount_options.max_size or sys.maxsize
        mount_options.free_space_required = mount_options.free_space_required or 100 * 1024 * 1024
        self._cache = FileCache(mount_options.data_dir,
                                mount_options.max_size,
                                mount_options.free_space_required,
                                self._download_stream,
                                self._get_handle)
        self._streaming_reader = StreamingReader(self._dataflow,
                                                 files_column,
                                                 self._mount_timestamp,
                                                 self._engine_api,
                                                 self._get_handle)
        self._open_dirs = {}
        self._handle = 0

    def _get_handle(self):
        self._handle += 1
        return self._handle

    def _list_entries(self, path: str) -> List[str]:
        if path[-1] != '/':
            # Ensure directories end with /
            path = path + '/'

        matching_streams = self._dataflow.filter(col(PORTABLE_PATH).starts_with(path)) \
            .add_column(col(PORTABLE_PATH).substring(len(path)), RELATIVE_PATH, PORTABLE_PATH) \
            .to_pandas_dataframe()

        entries = ['.', '..']
        if len(matching_streams) > 0:
            children = list(set([file.split('/')[0] for file in matching_streams[RELATIVE_PATH]]))
            children.sort()
            entries = entries + children

        return entries

    def _download_stream(self, stream_info: StreamInfo, target_path: str) -> int:
        def get_arguments(arguments):
            args = {}
            for name in arguments.keys():
                value = arguments[name]
                if isinstance(value, StreamInfo):
                    args[name] = get_stream_info_value(value)
                elif isinstance(value, str):
                    args[name] = { 'string': value }
                elif isinstance(value, bool):
                    args[name] = { 'boolean': value }
                elif isinstance(value, float):
                    args[name] = { 'double': value }
                elif isinstance(value, int):
                    args[name] = { 'long': value }
                else:
                    raise TypeError('Unexpected type "{}"'.format(type(value)))
            return args

        def get_stream_info_value(si):
            return {
                'streaminfo': {
                    'handler': si.handler,
                    'resourceidentifier': si.resource_identifier,
                    'arguments': get_arguments(si.arguments)
                }
            }

        stream_info_value = get_stream_info_value(stream_info)
        return self._engine_api.download_stream_info(
            DownloadStreamInfoMessageArguments(stream_info_value,
                                               target_path))

    def _get_stream_details_for_path(self, path) -> Optional[StreamDetails]:
        matching_rows = self._dataflow.filter(col(PORTABLE_PATH) == path) \
            .add_column(get_stream_properties(col(self._files_column)), STREAM_PROPERTIES, PORTABLE_PATH) \
            .add_column(col(STREAM_SIZE, col(STREAM_PROPERTIES)), STREAM_SIZE, STREAM_PROPERTIES) \
            .add_column(col(LAST_MODIFIED, col(STREAM_PROPERTIES)), LAST_MODIFIED, STREAM_SIZE) \
            .add_column(col(CAN_SEEK, col(STREAM_PROPERTIES)), CAN_SEEK, LAST_MODIFIED) \
            .to_pandas_dataframe(extended_types=True)
        if len(matching_rows) == 0:
            return None

        row = matching_rows.iloc[0]
        return StreamDetails(row[self._files_column],
                             row[PORTABLE_PATH],
                             row[STREAM_SIZE],
                             row[LAST_MODIFIED],
                             row[CAN_SEEK])

    def _cache_path(self, path: str):
        stream_details = self._get_stream_details_for_path(path)
        stream_last_modified = int(stream_details.last_modified.timestamp() if stream_details.last_modified is not None
                                   else self._mount_timestamp)
        stat = create_stat(S_IFREG,
                           stream_details.size,
                           stream_last_modified,
                           stream_last_modified,
                           stream_last_modified)
        self._cache.push(path, stream_details.stream_info, stat)

    def getattr(self, path, fh=None):
        log.debug('getattr(path=%s)', path, extra=dict(path=path))

        if path in self._cache:
            log.debug('Path found in cache.', path, extra=dict(path=path))
            return stat_to_dict(self._cache.get_attributes(path))

        try:
            log.debug('Attempting to stream attributes.', path, extra=dict(path=path))
            return stat_to_dict(self._streaming_reader.get_attributes(path))
        except UnknownStreamSizeError:
            log.debug('Unknown size for specified path.', path, extra=dict(path=path))
            self._cache_path(path)
            return stat_to_dict(self._cache.get_attributes(path))

    def opendir(self, path):
        log.debug('opendir(path=%s)', path)
        handle = self._get_handle()
        self._open_dirs[path] = self._list_entries(path)
        log.debug('Entries retrieved %s.', str(self._open_dirs[path]), extra=dict(handle=handle))
        return handle

    def readdir(self, path, fh):
        log.debug('readdir(path=%s, fh=%s)', path, fh, extra=dict(handle=fh))
        dir_entries = self._open_dirs.get(path)
        if dir_entries is None:
            log.warning('No entries found in cache. Was opendir not called?', extra=dict(handle=fh))
            dir_entries = self._list_entries(path)

        log.debug('Returning entries.', extra=dict(handle=fh))
        return dir_entries

    def releasedir(self, path, fh):
        try:
            log.info('releasedir(handle=%s)', fh)
            self._open_dirs.pop(path)
        except KeyError:
            log.warning('Failed to release directory.', extra=dict(handle=fh))
            log.error('Unexpected error during getattr.', exc_info=sys.exc_info())
            raise FuseOSError(ENOENT)

    def open(self, path, flags):
        log.debug('open(path=%s, flags=%s)', path, flags, extra=dict(path=path, flags=flags))

        if path not in self._cache:
            log.debug('Caching path: %s', path, extra=dict(path=path))
            self._cache_path(path)

        try:
            log.debug('Reading from cache: %s', path, extra=dict(path=path))
            handle = self._cache.open(path)
            log.debug('File opened from cache: %s (handle=%s)', path, handle, extra=dict(path=path, handle=handle))
            return handle
        except FuseOSError as e:
            log.debug('Error encountered while opening file: %s', path, extra=dict(path=path), exc_info=sys.exc_info())
            if e.errno != EFBIG:
                raise

        # If we failed because the file is too big to download, try to stream it
        log.debug('File too big to download. Streaming: %s', path, extra=dict(path=path))
        try:
            return self._streaming_reader.open(path)
        except Exception:
            log.debug('Failed to stream file: %s', path, extra=dict(path=path), exc_info=sys.exc_info())
            log.info('Failed to stream file.')
            raise

    def read(self, path, size, offset, fh):
        log.debug('read(path=%s, size=%s, offset=%s, fh=%s)',
                  path,
                  size,
                  offset,
                  fh,
                  extra=dict(path=path, size=size, offset=offset, fh=fh))

        if path in self._cache:
            log.debug('Reading file from cache: %s (handle=%s)', path, fh, extra=dict(path=path, handle=fh))
            return self._cache.read(fh, size, offset)
        else:
            log.debug('Streaming file read: %s (handle=%s)', path, fh, extra=dict(path=path, handle=fh))
            return self._streaming_reader.read(fh, size, offset)

    def release(self, path, fh):
        log.debug('release(path=%s, fh=%s)', path, fh, extra=dict(path=path, handle=fh))

        if path in self._cache:
            log.debug('Releasing file from cache: %s', path, fh, extra=dict(path=path, handle=fh))
            return self._cache.release(fh)
        else:
            log.debug('Releasing file from streaming reader: %s', path, fh, extra=dict(path=path, handle=fh))
            return self._streaming_reader.release(fh)

    def destroy(self, path):
        log.info('Tearing down mount.')
        self._cache.clear()


def mount(dataflow: Dataflow,
          files_column: str,
          mount_point: str,
          base_path: str = None,
          options: MountOptions = None,
          foreground=True) -> FUSE:
    return FUSE(_DPrepFuse(dataflow, files_column, base_path, options), mount_point, foreground=foreground)

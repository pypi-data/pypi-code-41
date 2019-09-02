# -*- coding: utf-8 -*-

import logging

import gddriver.utils.io as io_util
__all__ = [
    'Object',
    'Credential',
    'LoggerConfig',
    'DRIVER_LOGGER_CONFIG',
    'StreamTransferRequest',
    'FTPStreamUploadRequest',
    'OSSStreamUploadRequest',
    'AppendRequest',
    'StreamDownloadRequest',
    'DownloadResult',
    'StreamDownloadResult',
    'OperationResult',
    'UploadResult',
    'AppendResult',
    'RestoreResult',
    'CopyRequest',
    'OSSCopyRequest'
]


class LoggerConfig(object):

    _logger_name = "gddriver"

    def __init__(self):
        self._logger = logging.getLogger(self._logger_name)

    @property
    def logger(self):
        return self._logger

    @property
    def name(self):
        return self._logger_name


DRIVER_LOGGER_CONFIG = LoggerConfig()


class Object(object):
    def __init__(self, name, size=0, **kwargs):
        """
        对象元信息

        :param name: 对象名称 (必须是在容器中唯一的).
        :type  name: ``str``

        :param size: 对象大小（单位：字节）
        :type  size: ``int``

        :param kwargs: 对象的拓展信息，记录到extra中，根据不同的存储服务有不同的关键字

        extra
            + oss:
                * last_modified:    UNIX TIMPSTAMP
                * etag：            etag
                * object_type:      Normal Multipart Appendable ...
                * storage_class:    Standard Archive ...
                * restore:          是否为恢复/恢复中的归档文件 （get_object_meta时获得）
                * restore_finished: 是否恢复完成  （get_object_meta时获得）
                * expiry_date:      归档文件恢复的过期时间 （get_object_meta时获得）
            + ftp:
                * parent:         /root/prefix
                * is_file:        是否为文件
                * short_name:     对象名，没有前缀
        """
        self.name = name
        self.extra = {}
        self.size = size
        if kwargs:
            self.extra.update(**kwargs)

    @property
    def storage_class(self):
        return self.extra.get('storage_class', 'Standard')

    def __str__(self):
        return 'name: {name}, size: {size}, extra: {extra}'.format(
            name=self.name,
            size=self.size,
            extra=self.extra
        )


class Credential(object):
    def __init__(self, access_key_id=None, access_key_secret=None, access_key_token=None,
                 user=None, password=None):
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._access_key_token = access_key_token
        self._user = user
        self._password = password

    @property
    def access_key_id(self):
        return self._access_key_id

    @property
    def access_key_secret(self):
        return self._access_key_secret

    @property
    def access_key_token(self):
        return self._access_key_token

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @access_key_token.setter
    def access_key_token(self, v):
        self._access_key_token = v


class _Request(object):

    def __init__(self, container_name):
        self._container_name = container_name

    @property
    def container_name(self):
        """容器(Bucket)名称"""
        return self._container_name

    @container_name.setter
    def container_name(self, v):
        """容器(Bucket)名称"""
        self._container_name = v


class StreamTransferRequest(_Request):

    def __init__(self, container_name, stream, object_name):
        super(StreamTransferRequest, self).__init__(container_name)
        self._stream = stream
        self._object_name = object_name
        self._progress_callback = None
        self._checksum_type = None
        self._data_size = None

    @property
    def stream(self):
        """流式的数据，文件流、网络流、字符串等"""
        return self._stream

    @property
    def object_name(self):
        """对象名称"""
        return self._object_name

    @object_name.setter
    def object_name(self, v):
        self._object_name = v

    @property
    def checksum_type(self):
        """校验码类型[ md5|crc ]  str """
        return self._checksum_type

    @checksum_type.setter
    def checksum_type(self, v):
        self._checksum_type = v

    @property
    def progress_callback(self):
        """进度回调"""
        return self._progress_callback

    @progress_callback.setter
    def progress_callback(self, v):
        self._progress_callback = v

    @property
    def data_size(self):
        """预计的流大小，用于process_callback回调，当不传入时会尝试通过data的属性计算"""
        return self._data_size

    @data_size.setter
    def data_size(self, v):
        self._data_size = v


class FileTransferRequest(_Request):
    def __init__(self, container_name, file_path, object_name):
        super(FileTransferRequest, self).__init__(container_name)

        self._object_name = object_name
        self._file_path = file_path
        self._checksum_type = None
        self._threads_count = 1
        self._progress_callback = None

    @property
    def object_name(self):
        return self._object_name

    @property
    def file_path(self):
        """本地文件路径 str """
        return self._file_path

    @property
    def checksum_type(self):
        """设置校验码类型[ md5|crc ]  str """
        return self._checksum_type

    @property
    def threads_count(self):
        """线程数  int"""
        return self._threads_count

    @property
    def progress_callback(self):
        """进度回调"""
        return self._progress_callback

    @object_name.setter
    def object_name(self, v):
        self._object_name = v

    @file_path.setter
    def file_path(self, v):
        self._file_path = v

    @threads_count.setter
    def threads_count(self, v):
        self._threads_count = v

    @checksum_type.setter
    def checksum_type(self, v):
        self._checksum_type = v

    @progress_callback.setter
    def progress_callback(self, v):
        self._progress_callback = v


class OSSUploadRequest(FileTransferRequest):
    """
    OSS 上传请求，将本地文件上传到oss服务中
    """

    def __init__(self, container_name, file_path, object_name):
        super(OSSUploadRequest, self).__init__(container_name, file_path, object_name)

        self._headers = None
        self._part_size = None

    @property
    def headers(self):
        """可选参数，object的header信息 dict"""
        return self._headers

    @property
    def part_size(self):
        """分片传输时的每一批的大小"""
        return self._part_size

    @headers.setter
    def headers(self, v):
        self._headers = v

    @part_size.setter
    def part_size(self, v):
        self._part_size = v


class FTPUploadRequest(FileTransferRequest):
    """ FTP上传请求，将本地指定文件上传到FTP中

            * object_name: 不包含container目录

            * container_name: ftp中作为container的目录

            * object_name: 不包含container_name的ftp文件路径.

            * checksum_type: checksum type

            * threads_count: FTP无法并发上传文件，threads_count参数无影响

            * buffer_size: 调整ftp通信中传输的数据块大小

        """

    def __init__(self, container_name, file_path, object_name):
        super(FTPUploadRequest, self).__init__(container_name, file_path, object_name)
        self._buffer_size = None

    @property
    def buffer_size(self):
        """ftp上传中传输的数据块大小 int"""
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, v):
        self._buffer_size = v


class OSSDownloadRequest(FileTransferRequest):
    """
        OSS下载请求，从存储服务中下载到本地指定目录
    """
    pass


class FTPDownloadRequest(FileTransferRequest):

    """ FTP 下载请求，从ftp中下载文件到本地目录

        * object_name: 不包含container目录

        * container_name: 指定的作为容器的ftp目录

        * file_path: 文件的目标路径.

        """

    def __init__(self, container_name, file_path, object_name):
        super(FTPDownloadRequest, self).__init__(container_name, file_path, object_name)
        self._buffer_size = None

    @property
    def buffer_size(self):
        """ftp下载中传输的数据块大小 int"""
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, v):
        self._buffer_size = v


class FTPStreamUploadRequest(StreamTransferRequest):
    """FTP 流式上传请求，从本地上传一个流到FTP服务中"""
    pass


class OSSStreamUploadRequest(StreamTransferRequest):
    """ OSS流式上传请求 """
    def __init__(self, container_name, stream, object_name):
        super(OSSStreamUploadRequest, self).__init__(container_name, stream, object_name)
        self._multi = None

    @property
    def multi(self):
        """是否分片上传, 文件流较大时，可以使用multi参数通知driver使用分片上传 bool"""
        return self._multi

    @multi.setter
    def multi(self, v):
        self._multi = v


class AppendRequest(StreamTransferRequest):
    """ 追加上传请求

        关于追加上传position参数
        * 当Position值为0时，如果没有同名(Appendable) Object，或者同名(Appendable) Object长度为0，该请求成功；
        其他情况均视为Position和Object长度不匹配的情形。

        * 首次追加操作的position必须为0，后续追加操作的position是Object的当前长度。
          例如，第一次Append Object请求指定position值为0，content-length是65536；
          那么，第二次Append Object需要指定position为65536。

    """

    def __init__(self, container_name, stream, object_name, position):
        super(AppendRequest, self).__init__(container_name, stream, object_name)
        self._position = position

    @property
    def position(self):
        """ 续传文件的坐标，必须与存储服务中存在的文件大小相匹配， 新的可追加文件Position为0 int"""
        return self._position

    @position.setter
    def position(self, v):
        self._position = v


class CopyRequest(_Request):
    """从当前Container中拷贝一个Object到当指定的Container

    container_name: 原文件所在的容器
    """

    def __init__(self, container_name, object_name, dst_object_name, dst_container_name=None):
        super(CopyRequest, self).__init__(container_name)
        self._object_name = object_name
        self._dst_container_name = dst_container_name
        self._dst_object_name = dst_object_name

    @property
    def object_name(self):
        """原文件名 str"""
        return self._object_name

    @object_name.setter
    def object_name(self, v):
        self._object_name = v

    @property
    def dst_container_name(self):
        """目的容器，默认为当前容器 str"""
        return self._dst_container_name

    @dst_container_name.setter
    def dst_container_name(self, v):
        self._dst_container_name = v

    @property
    def dst_object_name(self):
        """目的文件名 str"""
        return self._dst_object_name

    @dst_object_name.setter
    def dst_object_name(self, v):
        self._dst_object_name = v


class OSSCopyRequest(CopyRequest):
    def __init__(self, container_name, object_name, dst_object_name, dst_container_name=None):
        super(OSSCopyRequest, self).__init__(container_name, object_name, dst_object_name, dst_container_name)
        self._headers = None
        self._multi_threshold = None

    @property
    def headers(self):
        """object header"""
        return self._headers

    @headers.setter
    def headers(self, v):
        """
        :type v: dict
        :return:
        """
        self._headers = v

    @property
    def multi_threshold(self):
        """设置使用分片复制的阈值"""
        return self._multi_threshold

    @multi_threshold.setter
    def multi_threshold(self, v):
        """

        :type v: int
        :return:
        """
        self._multi_threshold = v


class StreamDownloadRequest(_Request):
    """ 流式下载请求
    """

    def __init__(self, container_name, object_name):
        super(StreamDownloadRequest, self).__init__(container_name)
        self._object_name = object_name
        self._buffer_size = None
        self._progress_callback = None

    @property
    def object_name(self):
        """对象名称"""
        return self._object_name

    @object_name.setter
    def object_name(self, v):
        self._object_name = v

    @property
    def progress_callback(self):
        """进度回调"""
        return self._progress_callback

    @progress_callback.setter
    def progress_callback(self, v):
        self._progress_callback = v

    @property
    def buffer_size(self):
        """流式下载中，从流中取出的每个个数据块大小 int"""
        return self._buffer_size

    @buffer_size.setter
    def buffer_size(self, v):
        self._buffer_size = v


class FTPStreamDownloadRequest(StreamDownloadRequest):
    """ FTP 流式下载请求，获取一个可以持续取出数据的流 """
    pass


class OSSStreamDownloadRequest(StreamDownloadRequest):
    """ OSS 流式下载请求，获取一个可以持续取出数据的流 """
    def __init__(self, container_name, object_name, headers=None, byte_range=None):
        super(OSSStreamDownloadRequest, self).__init__(container_name, object_name)
        self._headers = headers
        self._byte_range = byte_range

    @property
    def headers(self):
        """可选参数，object的header信息 dict"""
        return self._headers

    @headers.setter
    def headers(self, v):
        self._headers = v

    @property
    def byte_range(self):
        """下载范围: (left, right)
            - byte_range 为 (0, 99)  -> 'bytes=0-99'，表示读取前100个字节
            - byte_range 为 (None, 99) -> 'bytes=-99'，表示读取最后99个字节
            - byte_range 为 (100, None) -> 'bytes=100-'，表示读取第101个字节到文件结尾的部分（包含第101个字节）
            - left 和 right均为整数时，0 <= left < right
        """
        return self._byte_range

    @byte_range.setter
    def byte_range(self, v):
        if not isinstance(v, tuple):
            raise TypeError('byte range must be `tuple` type')
        self._byte_range = v


class OperationResult(object):
    def __init__(self, **kwargs):
        self.extra = {}
        if kwargs:
            self.extra.update(**kwargs)

    def __str__(self):
        return "extra: {}".format(self.extra)


class DownloadResult(OperationResult):
    def __init__(self, server_checksum=None, client_checksum=None, checksum_type=None, **kwargs):
        super(DownloadResult, self).__init__(**kwargs)
        self.__server_checksum = server_checksum
        self.__client_checksum = client_checksum
        self.__checksum_type = checksum_type

    @property
    def server_checksum(self):
        return self.__server_checksum

    @property
    def client_checksum(self):
        return self.__client_checksum

    @property
    def checksum_type(self):
        return self.__checksum_type

    def __str__(self):
        info = 'server checksum: {server_checksum}, client checksum: {client_checksum}, ' \
               'checksum type: {checksum_type}. more - {super_str}'
        return info.format(
            server_checksum=self.server_checksum,
            client_checksum=self.client_checksum,
            checksum_type=self.checksum_type,
            super_str=super(DownloadResult, self).__str__()
        )


class StreamDownloadResult(DownloadResult):
    """
        iterable object
    """

    def __init__(self, iterator, length=None, **kwargs):
        super(StreamDownloadResult, self).__init__(**kwargs)
        self.iterator = iterator
        self._length = length
        # 覆盖super.__client_checksum, 通过iterator.
        self.__client_checksum = None

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        try:
            return next(self.iterator)
        except StopIteration:
            if isinstance(self.iterator, io_util.Adapter) and self.iterator.checksum:
                self.__client_checksum = self.iterator.checksum
            raise

    @property
    def client_checksum(self):
        return self.__client_checksum or super(StreamDownloadResult, self).client_checksum

    @property
    def stream(self):
        """将result通过适配器转为file like的对象"""
        return io_util.make_file_like_adapter(self)

    def __len__(self):
        """流的长度"""
        return self._length


class UploadResult(OperationResult):
    def __init__(self, checksum, checksum_type, **kwargs):
        super(UploadResult, self).__init__(**kwargs)
        self.__checksum = checksum
        self.__checksum_type = checksum_type

    def __str__(self):
        info = "checksum: {client_checksum}, type: {checksum_type}, more - {super_info}"
        return info.format(
            client_checksum=self.checksum,
            checksum_type=self.checksum_type,
            super_info=super(UploadResult, self).__str__()
        )

    @property
    def checksum(self):
        return self.__checksum

    @property
    def checksum_type(self):
        return self.__checksum_type


class AppendResult(UploadResult):
    """
    追加上传结果

        * next_position: 下次追加写的偏移 (next_position == object_meta.size)
    """
    def __init__(self, next_position, **kwargs):
        super(AppendResult, self).__init__(**kwargs)
        self.next_position = next_position

    def __str__(self):
        return "next_position: {next}, {super_info}".format(
            next=self.next_position,
            super_info=super(AppendResult, self).__str__()
        )


class RestoreResult(OperationResult):
    def __init__(self, finished, expiry_date=None, **kwargs):
        super(RestoreResult, self).__init__(**kwargs)
        self.finished = finished
        self.expiry_date = expiry_date

    def __str__(self):
        return "restore finished: {finished}, expiry date: {expiry_date}, {super_info}".format(
            finished=self.finished,
            expiry_date=self.expiry_date,
            super_info=super(RestoreResult, self).__str__()
        )


class PartUploadRequest(StreamTransferRequest):
    """
    分片上传请求

    :param stream: 待上传数据。
    """

    def __init__(self, container_name, stream, object_name, part_number, upload_id):

        super(PartUploadRequest, self).__init__(container_name, stream, object_name)
        self._part_num = part_number
        self._upload_id = upload_id

    @property
    def part_number(self):
        """分片号，最小值是1."""
        return self._part_num

    @property
    def upload_id(self):
        """分片上传ID"""
        return self._upload_id


class PartUploadResult(UploadResult):

    def __init__(self, part_info, **kwargs):
        super(PartUploadResult, self).__init__(**kwargs)
        self._part_info = part_info

    @property
    def part_info(self):
        """分片信息.
        :rtype: gddriver.models.PartInfo
        """
        return self._part_info


class PartInfo(object):
    def __init__(self, etag, part_number):
        """

        :type etag: str
        :type part_number: int
        """
        self._etag = etag
        self._part_num = part_number

    @property
    def part_number(self):
        """分片号，最小值是1."""
        return self._part_num

    @property
    def etag(self):
        """分片的ETag，用于合并分块"""
        return self._etag

    @staticmethod
    def sort_parts(parts):
        """为PartInfo列表排序,
        :type parts: list
        """

        def take_part_num(part):
            return part.part_number

        parts.sort(key=take_part_num)
        return parts

    def __str__(self):
        return "Part {}, ETag: {}".format(self.part_number, self.etag)


class CompleteMultipartUploadRequest(_Request):
    def __init__(self, container_name, object_name, upload_id, parts):
        """
        合并分片上传的结果
        :param container_name: bucket/容器名称
        :param object_name: 对象名称
        :param upload_id: 分片上传ID
        :param parts: 所有的分片列表，元素可以是字典或PartInfo
        """
        super(CompleteMultipartUploadRequest, self).__init__(container_name)
        self._object_name = object_name
        self._upload_id = upload_id
        self._parts = self._map_value(parts)

    @property
    def parts(self):
        """list of PartInfo"""
        return self._parts

    @parts.setter
    def parts(self, value):
        """`parts` must be a dict(etag=?, part_number=?) or gddriver.models.PartInfo
        :type value list of dict or list of PartInfo
        """

        self._parts = self._map_value(value)

    @property
    def upload_id(self):
        """分片上传ID"""
        return self._upload_id

    @property
    def object_name(self):
        return self._object_name

    @staticmethod
    def _map_value(args):
        def map_to_parts(v):
            if isinstance(v, PartInfo):
                return v
            elif not isinstance(v, dict):
                raise ValueError("Parameter `parts` must be a dict(etag=?, part_number=?) or gddriver.models.PartInfo")
            return PartInfo(**v)
        return list(map(map_to_parts, args))

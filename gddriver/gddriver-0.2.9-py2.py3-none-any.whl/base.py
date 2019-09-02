# -*- coding: utf-8 -*-

from __future__ import with_statement

import gddriver.models as models

# 32 MB
DEFAULT_MULTIPART_TRANSFER_THRESHOLD = 1 << 25

__all__ = [
    'Connection',
    'StorageDriver'
]


class Connection(object):
    """
     Storage Server连接的许可信息，Driver执行操作时，通过connection信息完成服务认证
    """

    def __init__(self, host, port, credential, **kwargs):
        self.host = host
        self.port = port
        self.credential = credential

    def get_client(self, container_name):
        """
          获取认证后的连接客户端。
          在没有关闭连接之前，get_client会复用已有的连接
        """
        raise NotImplementedError

    def clone(self):
        """
          复制一个Connection，避免使用同一个session.
        :return:
        :rtype: :class:`Connection`
        """
        raise NotImplementedError

    def close(self):
        """关闭连接"""
        raise NotImplementedError

    def __str__(self):
        return "Connection<host={}, port={}>".format(self.host, self.port)

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class StorageDriver(object):
    connection_class = Connection

    @classmethod
    def create_connection_manager(cls, store_host, store_port, credential, **kwargs):
        """
        创建一个新的连接器，不同的 DriverImpl 会自动初始化各自的 ConnectionImpl

        NOTE: 由于设计的原因，connection的定义不够清析，如今 connection == connection_manager == connector
        :param store_host:
        :param store_port:
        :param credential:
        :type  credential: :class:`gddriver.models.Credential`
        :rtype: gddriver.base.Connection
        """
        return cls.connection_class(store_host, store_port, credential, **kwargs)

    def __init__(self):
        self.logger = models.DRIVER_LOGGER_CONFIG.logger

    def get_object_meta(self, connection, object_name, container_name):
        """
        返回存储服务中获取的实例信息

        :param connection:
        :type  connection: :class:`Connection`

        :param container_name: Container name.
        :type  container_name: ``str``

        :param object_name: Object name.
        :type  object_name: ``str``

        :return: :class:`Object` instance.
        :rtype: :class:`gddriver.models.Object`
        """
        raise NotImplementedError

    def upload_file(self, connection, request):
        """
        通过路径上传文件

        :param connection:
        :type  connection: :class:`Connection`

        :param request: 文件上传请求
        :type request: :class:`gddriver.models.FileTransferRequest`

        :return: 上传成功的结果
        :rtype: :class:``gddriver.models.UploadResult``
        """

        raise NotImplementedError

    def upload_object_via_stream(self, connection, request):
        """
        流式上传

        :param connection:
        :type  connection: :class:`Connection`

        :param request: 流式上传请求
        :type request: :class:`gddriver.models.StreamTransferRequest`

        :return: 上传成功的结果
        :rtype: :class:``gddriver.models.UploadResult``

        """
        raise NotImplementedError

    def append_object(self, connection, request):
        """
        将一个流追加上传到指定的object中

        :param connection:
        :type  connection: :class:`Connection`

        :param request: 追加上传请求
        :type request: :class:`gddriver.models.AppendRequest`

        :rtype: ``gddriver.models.AppendResult``
        """
        raise NotImplementedError

    def download_file(self, connection, request):
        """
        下载文件到指定的路径

        :param connection:
        :type  connection: :class:`Connection`

        :param request: 文件下载请求
        :type request: :class:`gddriver.models.FileTransferRequest`

        """
        raise NotImplementedError

    def download_object_as_stream(self, connection, request):
        """
        返回一个流的生成器.

        :param connection:
        :type  connection: :class:`Connection`

        :param request: 流式下载请求
        :type request: :class:`gddriver.models.StreamDownloadRequest`

        :return: A generator of file chunk
        :rtype: :class:``gddriver.models.StreamDownloadResult``

        """
        raise NotImplementedError

    def copy_object(self, connection, request):
        """

        从当前Container中拷贝一个Object到当指定的Container


        :param connection:
        :type  connection: :class:`Connection`

        :param request: 原文件所在的容器(bucket)
        :type  request: :class:``gddriver.models.CopyRequest``

        :return:
        """
        raise NotImplementedError

    def archive_object(self, connection, src_container_name, src_object_name,
                       archive_container_name, archive_object_name, **kwargs):
        """

        从当前容器归档一个文件到目标容器


        :param connection:
        :type  connection: :class:`Connection`

        :param src_container_name: 原文件所在的容器
        :type  src_container_name: :class:`str`

        :param src_object_name: 原始对象名
        :type src_object_name: `str`

        :param archive_container_name: 目标容器
        :type archive_container_name: `str`

        :param archive_object_name: 目标对象名称
        :type archive_object_name: `str`

        """
        raise NotImplementedError

    def restore_object(self, connection, src_container_name, src_object_name):
        """
        :param connection:
        :type  connection: :class:`Connection`

        :param src_object_name: 原始对象名
        :type src_object_name: `str`

        :param src_container_name: 原文件所在的容器
        :type  src_container_name: :class:`str`

        :rtype: :class:`gddriver.models.RestoreResult`
        """
        raise NotImplementedError

    def move_object(self, connection, src_object_name, dst_object_name,
                    container_name=None, dst_container_name=None):
        """
        移动/重命名
        since gddriver 0.2.1

        :param connection:
        :type  connection: :class:`Connection`

        :param src_object_name: 原始对象名
        :type src_object_name: `str`

        :param dst_object_name: 目标对象名称
        :type dst_object_name: `str`

        :param container_name: 原文件所在的容器
        :type  container_name: :class:`str`

        :param dst_container_name: 目标容器（默认原始容器）
        :type dst_container_name: `str`

        """
        raise NotImplementedError

    def delete_object(self, connection, object_name, container_name):
        """
        删除对象

        :param container_name:
        :type container_name: `str`

        :param object_name: Object name.
        :type object_name: `str`

        :param connection: Destination container.
        :type connection: :class:`Connection`

        """
        raise NotImplementedError

    def batch_delete_objects(self, connection, object_name_list, container_name):
        """
        批量删除

        :param connection:
        :type  connection: :class:`Connection`

        :param object_name_list: 待删除列表
        :type object_name_list: list of str

        :param container_name: 容器名称
        :type  container_name: :class:`str`

        """
        raise NotImplementedError

    def list_container_objects(self, connection, container_name, prefix=None, **kwargs):
        """
        返回对象的列表

        :param connection:
        :type  connection: :class:`Connection`

        :param container_name: Destination container.
        :type container_name: :class:`str`

        :param prefix: object_name 的前缀
        :type  prefix: :class:`str`

        :return: A list of Object instances, next_marker.
        :rtype: ``list`` of :class:`Object` | ``str``
        """
        raise NotImplementedError

    def get_object_sign_url(self, connection, object_name, container_name=None, **kwargs):
        raise NotImplementedError

    def init_multipart_upload(self, connection, object_name, container_name=None, overwrite=False):
        """
        初始化分片上传

        :param connection:
        :type  connection: :class:`Connection`

        :param object_name:  Object name
        :type object_name: str

        :param container_name: Destination container.
        :type container_name: :class:`str`

        :param overwrite: Overwrite the exist file
        :type overwrite: bool

        :return: upload_id
        :rtype: str
        """
        raise NotImplementedError

    def upload_part(self, connection, request):
        """
        :param connection:
        :type  connection: :class:`Connection`

        :param request:  request object
        :type request: gddriver.models.PartUploadRequest

        :rtype: gddriver.models.PartUploadResult
        """
        raise NotImplementedError

    def complete_multipart_upload(self, connection, request):
        """
        :param connection:
        :type  connection: :class:`Connection`

        :param request:  request object
        :type request: gddriver.models.CompleteMultipartUploadRequest

        :rtype: gddriver.models.UploadResult
        """
        raise NotImplementedError

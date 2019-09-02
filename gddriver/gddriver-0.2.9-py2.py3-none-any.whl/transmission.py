# -*- coding: utf-8 -*-

import os

import gddriver
import gddriver.errors as errors
import gddriver.models as models
import gddriver.utils.io as ioutil

logger = models.DRIVER_LOGGER_CONFIG.logger
DEFAULT_MULTIPART_TRANSFER_THRESHOLD = 1 << 25  # 32 MB


class _CommonStreamUploadRequest(models.StreamTransferRequest):
    def __init__(self, container_name, stream, object_name):
        super(_CommonStreamUploadRequest, self).__init__(container_name, stream, object_name)
        self._multi = None

    @property
    def multi(self):
        """是否分片上传 bool"""
        return self._multi

    @multi.setter
    def multi(self, v):
        self._multi = v


def upload_object_from_file(connection, request, driver, multipart_transfer_threshold):
    """
    通过路径上传文件，当文件大小超过阈值时，使用分片上传的形式

    文件超过阈值时，由于分片并发上传，校验码的计算可能需要另启一个线程，
    但使用OSS上传并且要求crc64校验码时就不会有此情况，oss会在上传完成时，将crc64返回

    :param driver:  存储服务驱动
    :type  driver: `gddriver.base.StorageDriver`

    :param connection: 连接信息
    :type  connection: `gddriver.base.Connection`

    :param request: 传输请求
    :type  request: `gddriver.models.FileTransferRequest`

    :param multipart_transfer_threshold: 分片传输阈值
    :type  multipart_transfer_threshold: int

    :return:
    """

    final_multipart_threshold = multipart_transfer_threshold or DEFAULT_MULTIPART_TRANSFER_THRESHOLD
    file_path = request.file_path
    object_name = request.object_name

    file_size = os.path.getsize(file_path)
    if file_size < final_multipart_threshold:
        logger.debug("upload %s to %s via stream, data-size=%s", file_path, object_name, file_size)
        with open(file_path, 'rb') as f:
            # 流式上传时，data_size需要用户自定义或者用户的progress_callback有能力处理data_size为空的情况
            stream_request = _CommonStreamUploadRequest(
                container_name=request.container_name,
                stream=f,
                object_name=object_name
            )

            stream_request.checksum_type = request.checksum_type
            stream_request.progress_callback = request.progress_callback
            stream_request.data_size = file_size

            res = driver.upload_object_via_stream(
                request=stream_request,
                connection=connection
            )
            logger.debug("upload %s to %s via stream, data-size=%s, upload successfully",
                         file_path, object_name, file_size)
            return res

    else:
        logger.debug("upload %s to %s by file path, data-size=%s, threads_count=%s",
                     file_path, object_name, file_size, request.threads_count)
        res = driver.upload_file(
            connection=connection,
            request=request
        )
        logger.debug("finished upload %s to %s by file path, data-size=%s, "
                     "threads_count=%s, upload successfully",
                     file_path, object_name, file_size, request.threads_count)
        return res


def download_object_to_file(connection, request, driver,
                            multipart_transfer_threshold, overwrite_existing, delete_on_failure):
    """
        当文件大小超过阈值(threshold)时，会启用多分片并发下载，如果要求计算校验码，则需要额外的时间同步等待校验码计算完成。
    文件未超过阈值时，校验码可以在传输时一并完成计算。

    :param driver:  存储服务驱动
    :type  driver: `gddriver.base.StorageDriver`

    :param connection: 连接信息
    :type  connection: `gddriver.base.Connection`

    :param request: 传输请求
    :type  request: `gddriver.models.FileTransferRequest`

    :param multipart_transfer_threshold: 分片并发下载的阈值（字节）
    :type  multipart_transfer_threshold: ``int``

    :param overwrite_existing: 本地存在时覆盖
    :type  overwrite_existing: ``bool``

    :param delete_on_failure:  下载失败时删除
    :type  delete_on_failure: ``bool``

    :rtype: :class:`gddriver.models.DownloadResult`
    """
    file_path = request.file_path
    object_name = request.object_name
    final_threshold = multipart_transfer_threshold or DEFAULT_MULTIPART_TRANSFER_THRESHOLD
    checksum_type = request.checksum_type

    info = "Download {object_name} to {file_path}, container {container_name}".format(
        object_name=object_name,
        file_path=file_path,
        container_name=request.container_name
    )

    if os.path.isdir(file_path):
        raise errors.PathTypeConflict("%s, local path is a directory".format(info))

    if os.path.exists(file_path) and not overwrite_existing:
        raise errors.FileAlreadyExists("%s, file already exists".format(info))

    object_meta = driver.get_object_meta(
        connection=connection,
        object_name=object_name,
        container_name=request.container_name
    )
    logger.debug("download %s to %s, data-size-threshold: %s, object info: %s",
                 object_name, file_path, final_threshold, object_meta)

    if object_meta.size < final_threshold:
        stream_download_request = models.StreamDownloadRequest(
            container_name=request.container_name,
            object_name=object_name)

        readable_stream = driver.download_object_as_stream(
            request=stream_download_request,
            connection=connection
        )
        stream_adapter = ioutil.make_checksum_adapter(readable_stream, checksum_type)

        with open(file_path, 'wb') as file_:
            size = ioutil.copy_file(stream_adapter, file_)
            if size != object_meta.size and delete_on_failure:
                os.remove(file_path)
                raise errors.UnexpectedDownloadedSize(object_meta.size, size)

        # 部分服务可能会提供server_checksum (比如OSS提供crc_checksum)
        result = models.DownloadResult(
            server_checksum=readable_stream.server_checksum,
            client_checksum=stream_adapter.checksum,
            checksum_type=stream_adapter.checksum_type
        )
    else:
        driver.download_file(
            request=request,
            connection=connection
        )

        checksum_gen = ioutil.create_checksum_yield(
            file_path=file_path,
            checksum_type=checksum_type,
            logger=logger
        )
        checksum = next(checksum_gen)
        result = models.DownloadResult(
            client_checksum=checksum,
            checksum_type=checksum_type
        )
    logger.info("download %s to %s, container %s, download successfully.",
                object_name, file_path, request.container_name)
    return result


def get_object_append_position(connection, driver, object_name, container_name):
    """
    获取对象当前的长度，可用于append_object的position

    :param connection:
    :type  connection: ``gddriver.base.Connection``
    :param driver:
    :type  driver:  ``gddriver.base.StorageDriver``
    :param container_name:
    :type  container_name: ``str``
    :param object_name: Object name.
    :type object_name: ``str``

    :return: 对象长度/坐标
    :rtype: ``int``
    """
    try:
        object_meta = driver.get_object_meta(
            connection=connection,
            object_name=object_name,
            container_name=container_name
        )
        return object_meta.size
    except errors.NoSuchObject:
        return 0


class GenericOperator(object):
    """
    Generic operator: 根据provider初始化相应的driver，并通过host/port和credential等信息初始化connection manager等信息

    为什么创建一个这样的代理：
        1. 存在使用者不想关注如何创建driver、connection等信息（精简操作步骤）
        2. 存在使用者不想单独管理 connection 和 driver (减少参数)
        3. 支持使用with的上下文，在每次使用之后释放资源
    since gddriver 0.2.1
    """
    def __init__(self, provider, credential, host, port=None, **kwargs):
        """

        :type credential: gddriver.models.Credential
        :param provider: oss | ftp : see gddriver.providers.Provider
        :param host: store host
        :param port: store port
        :param kwargs: 附加信息用于初始化Connection，具体可接受何种附加信息可见 OSSConnection / FtpConnection等实现类
        """
        self._driver = gddriver.get_driver(provider=provider)
        self._connector = self._driver.create_connection_manager(
            store_host=host,
            store_port=port,
            credential=credential,
            **kwargs
        )

    def get_object_meta(self, object_name, container_name):
        """
        返回存储服务中获取的实例信息

        :param container_name: Container name.
        :type  container_name: ``str``

        :param object_name: Object name.
        :type  object_name: ``str``

        :return: :class:`Object` instance.
        :rtype: :class:`gddriver.models.Object`
        """
        return self._driver.get_object_meta(
            self._connector,
            object_name=object_name,
            container_name=container_name
        )

    def list_container_objects(self, container_name, prefix=None, **kwargs):
        """
        返回对象的列表

        :param container_name: Destination container.
        :type container_name: :class:`str`

        :param prefix: object_name 的前缀
        :type  prefix: :class:`str`

        :return: A list of Object instances, next_marker.
        :rtype: ``list`` of :class:`Object` | ``str``
        """
        return self._driver.list_container_objects(
            self._connector,
            container_name=container_name, prefix=prefix,
            **kwargs
        )

    def upload_file(self, request):
        """
        通过路径上传文件

        :param request: 文件上传请求
        :type request: :class:`gddriver.models.FileTransferRequest`

        :return: 上传成功的结果
        :rtype: :class:``gddriver.models.UploadResult``
        """
        return self._driver.upload_file(
            self._connector,
            request=request
        )

    def upload_object_via_stream(self, request):
        """
        流式上传

        :param request: 流式上传请求
        :type request: :class:`gddriver.models.StreamTransferRequest`

        :return: 上传成功的结果
        :rtype: :class:``gddriver.models.UploadResult``

        """
        return self._driver.upload_object_via_stream(
            self._connector,
            request=request
        )

    def download_file(self, request):
        """
        下载文件到指定的路径

        :param request: 文件下载请求
        :type request: :class:`gddriver.models.FileTransferRequest`

        """
        return self._driver.download_file(
            self._connector,
            request=request
        )

    def download_object_as_stream(self, request):
        """
        返回一个流的生成器.

        :param request: 流式下载请求
        :type request: :class:`gddriver.models.StreamDownloadRequest`

        :return: A generator of file chunk
        :rtype: :class:``gddriver.models.StreamDownloadResult``

        """
        return self._driver.download_object_as_stream(
            self._connector,
            request=request
        )

    def append_object(self, request):
        """
        将一个流追加上传到指定的object中

        :param request: 追加上传请求
        :type request: :class:`gddriver.models.AppendRequest`

        :rtype: ``gddriver.models.AppendResult``
        """
        return self._driver.append_object(
            self._connector,
            request=request
        )

    def archive_object(self, src_container_name, src_object_name, archive_container_name,
                       archive_object_name, **kwargs):
        """
        从当前容器归档一个文件到目标容器

        :param src_container_name: 原文件所在的容器
        :type  src_container_name: :class:`str`

        :param src_object_name: 原始对象名
        :type src_object_name: `str`

        :param archive_container_name: 目标容器
        :type archive_container_name: `str`

        :param archive_object_name: 目标对象名称
        :type archive_object_name: `str`

        :rtype: `boolean`
        """
        return self._driver.archive_object(
            self._connector,
            src_container_name=src_container_name,
            src_object_name=src_object_name,
            archive_container_name=archive_container_name,
            archive_object_name=archive_object_name,
            **kwargs)

    def delete_object(self, object_name, container_name):
        """
        删除对象

        :param container_name:
        :type container_name: `str`

        :param object_name: Object name.
        :type object_name: `str`
        """
        return self._driver.delete_object(
            self._connector,
            object_name=object_name,
            container_name=container_name
        )

    def restore_object(self, src_container_name, src_object_name):
        """
        :param src_object_name: 原始对象名
        :type src_object_name: `str`

        :param src_container_name: 原文件所在的容器
        :type  src_container_name: :class:`str`

        :rtype: :class:`gddriver.models.RestoreResult`
        """
        return self._driver.restore_object(
            self._connector,
            src_container_name=src_container_name,
            src_object_name=src_object_name
        )

    def move_object(self, src_object_name, dst_object_name, container_name=None, dst_container_name=None):
        """
         移动/重命名
         since gddriver 0.2.2

         :param src_object_name: 原始对象名
         :type src_object_name: `str`

         :param dst_object_name: 目标对象名称
         :type dst_object_name: `str`

         :param container_name: 原文件所在的容器
         :type  container_name: :class:`str`

         :param dst_container_name: 目标容器（默认原始容器）
         :type dst_container_name: `str`

        """
        return self._driver.move_object(
            connection=self._connector,
            src_object_name=src_object_name,
            dst_object_name=dst_object_name,
            container_name=container_name,
            dst_container_name=dst_container_name
        )

    def batch_delete_objects(self, object_name_list, container_name):
        """
        批量删除

        :param object_name_list: 待删除列表
        :type object_name_list: list of str

        :param container_name: 容器名称
        :type  container_name: :class:`str`

        """
        return self._driver.batch_delete_objects(
            self._connector,
            object_name_list=object_name_list,
            container_name=container_name
        )

    def copy_object(self, request):
        """

        从当前Container中拷贝一个Object到当指定的Container

        :param request: 原文件所在的容器(bucket)
        :type  request: :class:``gddriver.models.CopyRequest``

        :return:
        """
        return self._driver.copy_object(
            self._connector,
            request=request
        )

    def get_object_sign_url(self, object_name, container_name=None, **kwargs):
        return self._driver.get_object_sign_url(
            self._connector,
            object_name=object_name,
            container_name=container_name,
            **kwargs
        )

    def init_multipart_upload(self, container_name, object_name, **kwargs):
        """
        初始化分片上传
        since gddriver-0.2.4

        :param object_name:  Object name
        :type object_name: str

        :param container_name: Destination container.
        :type container_name: :class:`str`

        :keyword overwrite: 是否覆盖
        :return: upload_id
        :rtype: str
        """
        return self._driver.init_multipart_upload(
            connection=self._connector,
            container_name=container_name,
            object_name=object_name,
            **kwargs
        )

    def upload_part(self, request):
        """ 上传分片
        since gddriver-0.2.4

        :param request:  request object
        :type request: gddriver.models.PartUploadRequest

        :rtype: gddriver.models.PartUploadResult
        """
        return self._driver.upload_part(
            connection=self._connector,
            request=request
        )

    def complete_multipart_upload(self, request):
        """ 完成分片上传，合并所有分片
        since gddriver-0.2.4

        :param request:  request object
        :type request: gddriver.models.CompleteMultipartUploadRequest

        :rtype: gddriver.models.UploadResult
        """
        self._driver.complete_multipart_upload(
            connection=self._connector,
            request=request
        )

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connector:
            self._connector.close()

    def __getattribute__(self, item):
        """为operator添加与StorageDriver相同的函数，免去填写connection参数的过程
        当执行自匹配调用时，只接收kwargs参数
        """
        try:
            return super(GenericOperator, self).__getattribute__(item)
        except AttributeError:
            base_attr = self._driver.__getattribute__(item)

            def func(**kwargs):
                return base_attr(connection=self._connector, **kwargs)
            return func

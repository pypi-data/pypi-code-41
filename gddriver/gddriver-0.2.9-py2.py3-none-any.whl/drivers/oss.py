# -*- coding: utf-8 -*-

"""
OSSStorageDriver：
    * 列出Bucket中的Object
    * 获取Object的meta信息
    * 文件上传
    * 流式上传
    * 下载到本地文件
    * 流式下载
    * 复制
    * 删除
    * 批量删除
    * 归档
    * 恢复
    * 获取下载链接
统一使用crc64进行校验，不支持在request中自定义的``checksum_type``

"""

import datetime
import functools
import traceback

import oss2
import oss2.exceptions as oss_exc

import gddriver.base as base
import gddriver.errors as err
import gddriver.models as models
import gddriver.utils.io as ioutil
import gddriver.utils.time as timeutil

DEFAULT_DOWNLOAD_BUFFER_SIZE = 1 << 14  # 16MB 默认下载时的缓冲大小
DEFAULT_SIZE_PER_PART = 1 << 20  # 1MB 默认每块分片的字节大小
DEFAULT_MULTIPART_TRANSFER_THRESHOLD = 1 << 26  # 64MB 默认分片传输的阈值
DEFAULT_URL_EXPIRES = 3600 * 12  # 12小时  下载链接默认过期时间
DEFAULT_LIST_OBJECTS = 100  # 默认遍历时的max_object
LIST_DATA_MAX_OBJECTS = 1000  # list_container_objects 时最大可获取的object数量
OSS_MAX_PART_NUM = 10000  # 分片上传最大分片数
PUT_DATA_MAX_SIZE = 5 * (1 << 30)  # 5GB  调用PutData api最大允许的文件大小


def exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = models.DRIVER_LOGGER_CONFIG.logger

        try:
            return func(*args, **kwargs)
        except oss_exc.NotFound as e:
            logger.warning("oss not found error", exc_info=1)
            details = e.details or {}
            if e.code == oss_exc.NoSuchBucket.code:
                raise err.NoSuchContainer(details.get('BucketName'), **details)
            elif e.code == oss_exc.NoSuchKey.code:
                raise err.NoSuchObject(details.get('Key'), **details)
            else:
                raise err.NotFound(e.message, **details)
        except oss_exc.PositionNotEqualToLength as e:
            logger.warning("oss object position not equal to length, %s", traceback.format_exc())
            details = e.details or {}
            raise err.AppendPositionConflict(e.message, **details)
        except oss_exc.ServerError as e:
            # 4xx类型错误
            logger.warning("oss server error", exc_info=1)
            details = e.details or {}
            if e.status == 400:
                raise err.BadRequest(e.message, code=e.code, **details)
            if e.status == 403:
                raise err.Forbidden(e.message, code=e.code, **details)
            else:
                raise err.DriverServerException(e.message, e.status, code=e.code, **details)
        except oss_exc.OssError as e:
            logger.warning("oss error", exc_info=1)
            status = e.status
            details = e.details or {}
            if 'timeout' in str(e.body):
                raise err.RequestTimeout(e.body, status=status, **details)
            elif 'RequestError' in str(e.body):
                raise err.DriverRequestException(e.body, status=status, **details)
            else:
                raise err.StorageDriverException('unknown oss error: {}'.format(e), status=status, **details)

    return wrapper


class OSSConnection(base.Connection):
    def __init__(self, host, port, credential, timeout=None):
        super(OSSConnection, self).__init__(
            host=host,
            port=port,
            credential=credential
        )
        self.session = None
        self.connect_timeout = timeout

    def clone(self):
        return OSSConnection(
            host=self.host,
            port=self.port,
            credential=self.credential
        )

    def get_client(self, container_name):
        """
        获取OSS客户端 (Bucket实例)，可调用oss api

        :param container_name: 对应bucket_name
        :return: 返回bucket，在连接未关闭之前，会复用之前的连接池
        :rtype: :class:`oss2.Bucket`
        """
        access_key_token = self.credential.access_key_token
        access_key_id = self.credential.access_key_id
        access_key_secret = self.credential.access_key_secret

        if not access_key_token:
            auth = oss2.Auth(access_key_id, access_key_secret)
        else:
            auth = oss2.StsAuth(access_key_id, access_key_secret, access_key_token)

        # 在oss sdk中，如果传入session，则复用会话，否则新开始一个会话
        oss_bucket = oss2.Bucket(auth, self.host, container_name,
                                 session=self.session,
                                 connect_timeout=self.connect_timeout
                                 )
        self.session = self._get_session(oss_bucket)
        return oss_bucket

    def close(self):
        self.session = None

    @classmethod
    def _get_session(cls, oss_bucket):
        # 避免oss2模块升级后不提供session直接获取
        if hasattr(oss_bucket, 'session'):
            return oss_bucket.session
        return None


class OSSStorageDriver(base.StorageDriver):

    connection_class = OSSConnection
    checksum_type = 'crc'

    def __init__(self):
        super(OSSStorageDriver, self).__init__()

    @exception_handler
    def get_object_meta(self, connection, object_name, container_name):
        """
        获取object的详细信息
           *  name
           *  size
           *  extra
                * last_modified:    最后修改时间，ISO 8601格式
                * etag：            oss附带的etag信息
                * object_type:      对象的上传类型： Normal Multipart Appendable ...
                * storage_class:    对象的存储类型： Standard Archive ...
                * restore_status:   '' / restoring / restored
                * expiry_date:      归档文件恢复的过期时间，ISO 8601格式

        :param connection: `OSSConnection` instance
        :type  connection: :class:`OSSConnection`

        :param object_name: 对象名称
        :type  object_name: `str`

        :param container_name: bucket name
        :type  container_name: :class:`str`

        :return: 返回Object meta信息
        :rtype: :class:``gddriver.models.Object``
        """
        bucket = connection.get_client(container_name)
        meta = bucket.head_object(object_name)
        storage_class, restore_status, expiry_date = self.get_restore_status(meta)
        last_modified = datetime.datetime.fromtimestamp(meta.last_modified) if meta.last_modified else None
        extra = {
            "etag": meta.etag,
            "last_modified": last_modified,
            "object_type": meta.object_type,
            "storage_class": storage_class,
            "restore_status": restore_status,
            "expiry_date": expiry_date
        }
        crc = meta.resp.headers.get('x-oss-hash-crc64ecma', '')
        if crc:
            extra['crc64'] = crc

        # 不论正常返回200 OK还是非正常返回，HeadObject都不返回消息体
        # 如果文件类型为符号链接， 响应头中Content-Length、ETag、Content-Md5均为目标文件的元信息；
        # Last - Modified是目标文件和符号链接的最大值；其他均为符号链接元信息。
        # OSS服务根据协议RFC 1864对消息内容（不包括头部）计算MD5值获得128比特位数字，
        # 对该数字进行base64编码为一个消息的Content-MD5值
        md5 = meta.resp.headers.get('content-md5', '')
        if md5:
            extra['content-md5'] = md5
        return models.Object(object_name, meta.content_length, **extra)

    @exception_handler
    def list_container_objects(self, connection, container_name, prefix=None,
                               marker='', max_objects=DEFAULT_LIST_OBJECTS):
        """
        列出容器中的object

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param container_name: bucket name
        :type  container_name: :class:`str`

        :param prefix: 文件的前缀（OSS中没有真正的目录的概念）
        :type  prefix: :class:`str`

        :param marker:  上一次遍历的标记，若marker不为None，则继续上一次标记遍历
        :type  marker: :class:`str`

        :param max_objects: 每次list返回的Object数目限制，最大可设置为1000
        :type  max_objects:  :class:`int`

        :return: object-meta列表, 下一次继续遍历的标记.
        :rtype: ``list`` of :class:`Object` | ``str``
        """
        _max_objects = max_objects if max_objects < LIST_DATA_MAX_OBJECTS else LIST_DATA_MAX_OBJECTS
        prefix = prefix or ''
        bucket = connection.get_client(container_name)
        result = bucket.list_objects(
            prefix=prefix,
            marker=marker,
            max_keys=_max_objects
        )
        is_truncated = result.is_truncated
        next_marker = None
        if is_truncated:
            next_marker = result.next_marker
        objects = []
        for meta in result.object_list:
            extra = {
                "etag": meta.etag,
                "last_modified": meta.last_modified,
                "object_type": meta.type,
                "storage_class": meta.storage_class
            }
            objects.append(models.Object(meta.key, meta.size, **extra))
        return objects, next_marker

    @exception_handler
    def download_object_as_stream(self, connection, request):
        """
        流式下载，获取一个可读的文件流
        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param request: 流式下载请求
        :type  request: gddriver.models.OSSStreamDownloadRequest

        :return: 返回的StreamDownloadResult是一个流，属性中默认包含从server端获取的crc
        :rtype: :class:``StreamDownloadResult``
        """
        logger = self.logger
        buffer_size = request.buffer_size
        container_name = request.container_name
        object_name = request.object_name
        progress_callback = request.progress_callback

        byte_range = request.byte_range if hasattr(request, 'byte_range') else None
        headers = request.headers if hasattr(request, "headers") else None

        buffer_size = buffer_size or DEFAULT_DOWNLOAD_BUFFER_SIZE
        object_meta = self.get_object_meta(connection, object_name, container_name)
        data_size = get_range_size(object_meta.size, byte_range)

        bucket = connection.get_client(container_name)
        stream = bucket.get_object(
            key=object_name,
            byte_range=byte_range,
            headers=headers
        )
        crc = stream.server_crc

        msg_template = ("download object as stream, bucket={}, object-key={}, "
                        "object-size={}, server-crc={}, buffer-size={}")
        msg = msg_template.format(container_name, object_name, object_meta.size, crc, buffer_size)
        logger.debug(msg)

        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        def generator():
            while True:
                chunk = stream.read(buffer_size)
                if not chunk:
                    break
                yield chunk
            logger.debug("%s, elapsed=%s, download finished", msg, stopwatch.elapsed())

        checksum_type = 'crc'
        stream_generator = generator()
        wrapped_stream = ioutil.make_progress_adapter(stream_generator, progress_callback, data_size)
        checksum_wrapped_stream = ioutil.make_checksum_adapter(wrapped_stream, checksum_type)
        result = models.StreamDownloadResult(
            iterator=checksum_wrapped_stream,
            length=data_size,
            server_checksum=crc,
            checksum_type=checksum_type
        )
        return result

    @exception_handler
    def download_file(self, connection, request):
        """
        下载文件到指定的路径中，支持断点续传

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param request: 流式下载请求
        :type  request: gddriver.models.OSSDownloadRequest

        """

        container_name = request.container_name
        object_name = request.object_name
        local_file_path = request.file_path
        threads_count = request.threads_count
        progress_callback = request.progress_callback

        msg_template = ("multipart download, bucket={container_name}, object-key={object_name}, "
                        "dst-path={file_path}, threads_count={threads_count}")
        msg = msg_template.format(
            container_name=container_name,
            object_name=object_name,
            file_path=local_file_path,
            threads_count=threads_count
        )
        self.logger.info(msg)

        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        bucket = connection.get_client(container_name)
        oss2.resumable_download(
            bucket=bucket,
            key=object_name,
            filename=local_file_path,
            num_threads=threads_count,
            progress_callback=progress_callback
        )
        self.logger.info("%s, elapsed=%s, download finished", msg, stopwatch.elapsed())

    @exception_handler
    def upload_object_via_stream(self, connection, request):
        """
        流式上传，可以上传网络流、文件流、字符串、bytes等可迭代的对象。

        :param connection: `OSSConnection` 实例
        :type  connection: :class:`OSSConnection`

        :param request:
        :type  request: `gddriver.models.OSSStreamUploadRequest`

        :rtype: :class:``gddriver.models.UploadResult``
        """

        container_name = request.container_name
        object_name = request.object_name
        stream = request.stream
        progress_callback = request.progress_callback

        data_size = request.data_size
        # 这是因为流式上传时，无法感知这个流的实际大小，默认会使用常规的put_object
        # 上传，但这种方式最大只能上传5GB文件，超过5GB必须使用分片上传，所以用户在知道
        # 文件流较大时，可以使用multi参数通知driver使用分片上传
        multi = request.multi if hasattr(request, 'multi') else False

        logger = self.logger
        msg_template = ("upload via stream, bucket={container_name}, object-key={object_name}, "
                        "checksum-type={checksum_type}, data-size={data_size}, multi={multi}")
        msg = msg_template.format(
            container_name=container_name,
            object_name=object_name,
            checksum_type=self.checksum_type,
            data_size=data_size,
            multi=multi
        )
        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        logger.info(msg)

        wrapped_stream = ioutil.make_progress_adapter(stream, progress_callback, data_size)

        bucket = connection.get_client(container_name)
        if not multi:
            oss_result = bucket.put_object(object_name, wrapped_stream)
        else:
            # 分片上传
            logger.info("%s, via multipart mode", msg)
            upload_id = bucket.init_multipart_upload(object_name).upload_id
            parts = []
            part_num = 0
            for chunk in wrapped_stream:
                part_num += 1
                result = bucket.upload_part(object_name, upload_id, part_num, chunk)
                parts.append(oss2.models.PartInfo(part_num, result.etag))
            oss_result = bucket.complete_multipart_upload(object_name, upload_id, parts)

        server_checksum = oss_result.crc
        extra = self.__get_extra_info(oss_result)
        result = models.UploadResult(
            checksum=server_checksum,
            checksum_type=self.checksum_type,
            **extra
        )
        logger.info('%s, checksum=%s, elapsed=%s, upload finished',
                    msg, result.checksum, stopwatch.elapsed())
        return result

    @exception_handler
    def upload_file(self, connection, request):
        """
        分片多线程上传一个文件

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param request:
        :type  request: `gddriver.models.OSSUploadRequest`

        :return:
        :rtype `UploadResult`
        """
        container_name = request.container_name
        file_path = request.file_path
        object_name = request.object_name
        threads_count = request.threads_count
        progress_callback = request.progress_callback

        part_size = request.part_size if hasattr(request, 'part_size') else None
        headers = request.headers if hasattr(request, 'headers') else None

        logger = self.logger
        msg_template = ("multipart upload, file={file_path}, bucket={container_name}, object-key={object_name}, "
                        "threads_count={threads_count}, part-size={part_size}, checksum-type={checksum_type}")
        msg = msg_template.format(
            file_path=file_path,
            container_name=container_name,
            object_name=object_name,
            threads_count=threads_count,
            part_size=part_size,
            checksum_type=self.checksum_type
        )
        logger.info(msg)

        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        bucket = connection.get_client(container_name)
        oss_result = oss2.resumable_upload(
            bucket=bucket,
            key=object_name,
            filename=file_path,
            headers=headers,
            part_size=part_size,
            progress_callback=progress_callback,
            num_threads=threads_count
        )

        server_checksum = oss_result.crc
        extra = self.__get_extra_info(oss_result)
        result = models.UploadResult(
            checksum=server_checksum,
            checksum_type=self.checksum_type,
            **extra
        )
        logger.info('{}, checksum={}, elapsed={}, upload finished'.format(
            msg, server_checksum, stopwatch.elapsed())
        )
        return result

    @exception_handler
    def append_object(self, connection, request):
        """
        追加上传，可以将网络流、文件流等追加到指定的object_name, 最大不能超过5G

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param request:
        :type  request: `gddriver.models.AppendRequest`

        :return: 追加上传的结果 （返回的校验码为追加後整个文件的校验码）
        :rtype: :class:``gddriver.models.AppendResult``
        """

        container_name = request.container_name
        object_name = request.object_name
        stream = request.stream
        progress_callback = request.progress_callback
        position = request.position
        data_size = request.data_size

        logger = self.logger
        msg_template = ("append object, bucket={container_name}, object-name={object_name}, "
                        "position={position}, data-size={data_size}, checksum-type={checksum_type}")
        msg = msg_template.format(
            container_name=container_name,
            object_name=object_name,
            position=position,
            data_size=data_size,
            checksum_type=self.checksum_type
        )
        logger.info(msg)
        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        bucket = connection.get_client(container_name)
        progress_wrapped_stream = ioutil.make_progress_adapter(stream, progress_callback, data_size)

        init_crc = 0
        if position != 0:
            try:
                object_meta = self.get_object_meta(
                    connection=connection,
                    container_name=container_name,
                    object_name=object_name
                )
                init_crc = object_meta.extra.get('crc64', None)
            except err.NoSuchObject:
                # 用户追加上传到一个不存在的文件时，但position不为0，捕获异常，oss重新抛出後由装饰器统一处理
                logger.debug('append object not found: %s', msg)
        oss_result = bucket.append_object(object_name, position, progress_wrapped_stream, init_crc=init_crc)
        server_checksum = oss_result.crc

        next_position = oss_result.next_position
        extra = self.__get_extra_info(oss_result)
        result = models.AppendResult(
            next_position=next_position,
            checksum=server_checksum,
            checksum_type=self.checksum_type,
            **extra
        )
        logger.info("%s, checksum=%s, elapsed=%s, upload finished",
                    msg, server_checksum, stopwatch.elapsed())
        return result

    @exception_handler
    def delete_object(self, connection, object_name, container_name=None):
        bucket = connection.get_client(container_name)
        bucket.delete_object(object_name)

    @exception_handler
    def copy_object(self, connection, request):
        """
        复制文件
          复制文件较大时，必须调整part_size从而保证总分片数不超过10000 (OSS限制)

          OSS相关限制条件：
            请求者必须对源Object有读权限。
            源Object和目标Object必须属于同一个地域（数据中心）。
            不能拷贝通过追加上传方式产生的Object。
            如果源Object为符号链接，只拷贝符号链接，不拷贝符号链接指向的文件内容。

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param request: 对象复制请求
        :type  request: :class:``gddriver.models.OSSCopyRequest``
        :return:
        """

        logger = self.logger

        src_container_name = request.container_name
        src_object_name = request.object_name
        # 默认复制到当前容器中
        dst_container_name = request.dst_container_name or src_container_name
        dst_object_name = request.dst_object_name

        # 兼容基类的参数
        headers = request.headers if hasattr(request, 'headers') else None
        multi_threshold = request.multi_threshold if hasattr(request, 'multi_threshold') else None
        final_threshold = multi_threshold or DEFAULT_MULTIPART_TRANSFER_THRESHOLD

        object_meta = self.get_object_meta(connection, src_object_name, src_container_name)

        msg_template = ("copy object, from={src_container_name}:{src_object_name}, "
                        "to={dst_container_name}:{dst_object_name}, size={size}")
        msg = msg_template.format(
            src_container_name=src_container_name,
            src_object_name=src_object_name,
            dst_container_name=dst_container_name,
            dst_object_name=dst_object_name,
            size=object_meta.size
        )
        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        dst_bucket = connection.get_client(dst_container_name)
        if object_meta.size <= final_threshold:
            logger.info(msg)
            dst_bucket.copy_object(
                source_bucket_name=src_container_name,
                source_key=src_object_name,
                target_key=dst_object_name,
                headers=headers
            )
        else:
            # 文件较大时，使用分片复制
            upload_id = dst_bucket.init_multipart_upload(dst_object_name).upload_id
            part_size = regulate_part_size(object_meta.size)

            logger.info("%s, multipart copy, upload-id=%s, part-size=%s", msg, upload_id, part_size)
            parts = []
            part_number = 1
            offset = 0
            while offset < object_meta.size:
                parts_to_upload = min(part_size, object_meta.size - offset)
                # 左闭右闭
                byte_range = (offset, offset + parts_to_upload - 1)
                part_copy_result = dst_bucket.upload_part_copy(
                    source_bucket_name=src_container_name,
                    source_key=src_object_name,
                    byte_range=byte_range,
                    target_key=dst_object_name,
                    target_upload_id=upload_id,
                    target_part_number=part_number
                )
                parts.append(oss2.models.PartInfo(part_number, part_copy_result.etag))
                offset += parts_to_upload
                part_number += 1
            logger.info("%s %s copied  elapsed=%s, finished", msg, offset, stopwatch.elapsed())
            dst_bucket.complete_multipart_upload(dst_object_name, upload_id, parts)

    @exception_handler
    def batch_delete_objects(self, connection, object_name_list, container_name=None):
        """批量删除文件。

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param container_name: bucket name
        :type  container_name: :class:`str`

        :param object_name_list:
        :type object_name_list: list of str

        """
        logger = self.logger
        logger.info("batch delete objects, %s", object_name_list)
        if not object_name_list:
            logger.warning("object key list is None.")
            return
        # TODO 确认批量删除部分失败的场景
        bucket = connection.get_client(container_name)
        batch_delete_result = bucket.batch_delete_objects(object_name_list)
        logger.info("batch delete objects, result=%s", batch_delete_result)

    @exception_handler
    def archive_object(self, connection, src_container_name, src_object_name,
                       archive_container_name, archive_object_name, delete=False):
        """
        将文件从一个bucket中转归档到另一个bucket中，并删除原来的文件，适合不同类型的bucket之间的复制

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param src_container_name: 原数据的bucket name
        :param src_object_name: 原数据的object_key
        :param archive_container_name: 要归档至的bucket name
        :param archive_object_name: 归档后的object key
        :param delete: 是否在归档完成后删除原文件
        """
        self.__download_and_upload_between_buckets(
            connection=connection,
            src_bucket_name=src_container_name,
            src_obj_key=src_object_name,
            dst_bucket_name=archive_container_name,
            dst_obj_key=archive_object_name
        )
        if delete:
            self.delete_object(
                connection=connection,
                container_name=src_container_name,
                object_name=src_object_name
            )

    @exception_handler
    def restore_object(self, connection, src_container_name, src_object_name):
        """
        将低频存储类型暂时恢复为可访问的类型
        :param connection: `OSSConnection`
        :param src_container_name: 原数据的bucket name
        :param src_object_name: 原数据的object_key
        :rtype: :class:``gddriver.models.RestoreResult``
        """

        archive_bucket = connection.get_client(src_container_name)
        try:
            self.logger.info('restore: %s start', src_object_name)
            rsp = archive_bucket.restore_object(src_object_name)
            self.logger.info('restore: %s finished, response status: %s', src_object_name, rsp.status)
            if rsp.status == 202:
                return models.RestoreResult(finished=False)
        except oss_exc.RestoreAlreadyInProgress:
            self.logger.info("restore already in process: %s/%s", src_container_name, src_object_name)
            return models.RestoreResult(finished=False)

        meta = archive_bucket.head_object(src_object_name)
        _, restore_status, expiry_date = self.get_restore_status(meta)
        finished = restore_status == 'restored'
        return models.RestoreResult(
            finished=finished,
            expiry_date=expiry_date
        )

    @exception_handler
    def move_object(self, connection, src_object_name, dst_object_name, container_name=None, dst_container_name=None):
        """
        将object移动到另一路径（不支持从标准存储向低频存储中移动，如有需要，则使用archive_object），

        :param connection: `OSSConnection`
        :type  connection: :class:`OSSConnection`

        :param container_name: 原数据的bucket name
        :param src_object_name: 原数据的object_key
        :param dst_object_name: 要归档至的bucket name
        :param dst_container_name: 归档后的object key
        """
        copy_request = models.OSSCopyRequest(
            container_name=container_name,
            object_name=src_object_name,
            dst_container_name=dst_container_name or container_name,
            dst_object_name=dst_object_name
        )

        object_meta = self.get_object_meta(
            connection=connection,
            container_name=copy_request.container_name,
            object_name=copy_request.object_name
        )
        if object_meta.extra.get('object_type') == 'Appendable':
            # Append类型的文件move之后仍然是Append类型
            self._copy_append_type_object(
                connection=connection,
                copy_request=copy_request,
                object_meta=object_meta
            )
        else:
            self.copy_object(
                connection=connection,
                request=copy_request
            )
        self.delete_object(
            connection=connection,
            container_name=container_name,
            object_name=src_object_name
        )

    @exception_handler
    def get_object_sign_url(self, connection, object_name, container_name=None, expires=DEFAULT_URL_EXPIRES,
                            headers=None):
        """

        :param connection:
        :param object_name:
        :param container_name:
        :param headers: 需要签名的HTTP头部，如名称以x-oss-meta-开头的头部（作为用户自定义元数据）、
                        Content-Type头部等。对于下载，不需要填。
        :param expires:  过期时间 (秒)
        :return:
        """
        bucket = connection.get_client(container_name)
        expires = expires or DEFAULT_URL_EXPIRES
        return bucket.sign_url('GET', object_name, expires=expires, headers=headers)

    @exception_handler
    def init_multipart_upload(self, connection, object_name, container_name=None, overwrite=False):
        """
        :param connection:
        :type connection: OSSConnection
        :param object_name:
        :param container_name:
        :param overwrite: 默认直接覆盖上传，如非覆盖，则抛出文件已存在的异常
        :return:
        """

        if not overwrite:
            try:
                self.get_object_meta(
                    container_name=container_name,
                    connection=connection,
                    object_name=object_name
                )
                raise err.FileAlreadyExists("{} already exists".format(object_name))
            except err.NotFound:
                pass

        bucket = connection.get_client(container_name)
        result = bucket.init_multipart_upload(object_name)
        self.logger.debug(result)
        return result.upload_id

    @exception_handler
    def upload_part(self, connection, request):

        bucket = connection.get_client(request.container_name)
        oss_response = bucket.upload_part(
            key=request.object_name,
            upload_id=request.upload_id,
            part_number=request.part_number,
            data=request.stream,
            progress_callback=request.progress_callback
        )
        return models.PartUploadResult(
            checksum=oss_response.crc,
            checksum_type='crc',
            part_info=models.PartInfo(part_number=request.part_number, etag=oss_response.etag)
        )

    @exception_handler
    def complete_multipart_upload(self, connection, request):

        def map_to_oss_part_info(part):
            """
            :type part: gddriver.models.PartInfo
            """
            return oss2.models.PartInfo(part.part_number, part.etag)

        bucket = connection.get_client(request.container_name)
        parts = map(map_to_oss_part_info, request.parts)
        models.PartInfo.sort_parts(list(parts))
        oss_result = bucket.complete_multipart_upload(request.object_name, request.upload_id, parts)
        self.logger.debug(oss_result)

    def _copy_append_type_object(self, connection, copy_request, object_meta=None):
        """
        object type 为Append 的情况下，无法直接使用copy，需通过流式传输复制文件

        :type connection: OSSConnection
        :type copy_request: gddriver.models.CopyRequest
        """

        self.logger.debug("copy APPEND object from %s to %s, src container: %s, dst container: %s",
                          copy_request.object_name, copy_request.dst_object_name,
                          copy_request.container_name, copy_request.dst_container_name)

        if not object_meta:
            object_meta = self.get_object_meta(
                connection=connection,
                container_name=copy_request.container_name,
                object_name=copy_request.object_name
            )

        object_size = object_meta.size
        part_size = regulate_part_size(object_size)

        stream_download_request = models.OSSStreamDownloadRequest(
            container_name=copy_request.container_name,
            object_name=copy_request.object_name
        )
        stream_download_request.buffer_size = part_size

        stream = self.download_object_as_stream(
            connection=connection,
            request=stream_download_request
        )

        append_request = models.AppendRequest(
            container_name=copy_request.dst_container_name,
            object_name=copy_request.dst_object_name,
            stream=stream,
            position=0
        )
        result = self.append_object(
            connection=connection,
            request=append_request
        )
        self.logger.debug("copy APPEND object from %s to %s, src container: %s, dst container: %s, result: %s",
                          copy_request.object_name, copy_request.dst_object_name,
                          copy_request.container_name, copy_request.dst_container_name, result)
        self.logger.debug("copy")

    def __download_and_upload_between_buckets(self, connection, src_bucket_name, src_obj_key,
                                              dst_bucket_name, dst_obj_key):

        # TODO 50GB的文件相当于每个分块至少5MB，并发量大时对性能消耗比较大

        msg = ("copy between buckets, from={src_bucket_name}:{src_obj_key}, "
               "to={dst_bucket_name}:{dst_obj_key}").format(
            src_bucket_name=src_bucket_name,
            src_obj_key=src_obj_key,
            dst_bucket_name=dst_bucket_name,
            dst_obj_key=dst_obj_key
        )
        self.logger.info(msg)

        object_meta = self.get_object_meta(
            connection=connection,
            container_name=src_bucket_name,
            object_name=src_obj_key
        )

        object_size = object_meta.size
        multi_part_upload = object_size > PUT_DATA_MAX_SIZE
        part_size = regulate_part_size(object_size)

        msg = "{}, size={}, chunk-size={}".format(msg, object_size, part_size)
        self.logger.info(msg)
        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        stream_download_request = models.OSSStreamDownloadRequest(
            container_name=src_bucket_name,
            object_name=src_obj_key
        )
        stream_download_request.buffer_size = part_size

        stream = self.download_object_as_stream(
            connection=connection,
            request=stream_download_request
        )

        stream_upload_request = models.OSSStreamUploadRequest(
            container_name=dst_bucket_name,
            stream=stream,
            object_name=dst_obj_key
        )
        stream_upload_request.multi = multi_part_upload

        result = self.upload_object_via_stream(
            connection=connection,
            request=stream_upload_request
        )
        self.logger.info("%s, result=%s, elapsed=%s, copy finished", msg, result, stopwatch.elapsed())
        return result

    @classmethod
    def _verify_and_get_server_checksum(cls, message, oss_result, client_checksum):
        """验证校验码，并将服务端校验码返回"""
        server_checksum = oss_result.crc
        if server_checksum != client_checksum:
            raise err.ChecksumMismatch(
                message=message,
                server_checksum=server_checksum,
                client_checksum=client_checksum
            )
        return server_checksum

    @staticmethod
    def __get_extra_info(result):
        """
        :param result: oss api请求的返回值
        :rtype: dict
        """
        return {'request_id': result.request_id, 'etag': result.etag}

    @classmethod
    def get_restore_status(cls, meta):
        """
        通过meta获取restore的状态信息
        :param meta:
        :type meta: :class:``oss2.models.HeadObjectResult``
        :return: 存储类型， restore状态， 过期时间
        :rtype: str | str | datetime.datetime
        """
        storage_class, restore, finished, expiry_date = cls.__get_restored_info(meta)
        # 普通文件
        if storage_class != oss2.BUCKET_STORAGE_CLASS_ARCHIVE:
            return storage_class, '', None
        # archived
        elif not restore:
            return storage_class, 'archived', None
        # restoring or restored
        elif finished:
            return storage_class, 'restored', expiry_date
        else:
            return storage_class, 'restoring', None

    @classmethod
    def __get_restored_info(cls, meta):
        """
        当文件非restoring或restored状态的文件，返回的第二个参数restore 为False，
        is_finished 为False，expiry_date 为None

        :param meta: meta of head_object
        :return: storage_class, is_restore_object, is_finished_restore, expiry
        """
        finished = False
        restore = False
        expiry_date = None

        # 如果Bucket类型为Archive，且用户已经提交Restore请求，则响应头中会以x-oss-restore返回该Object的Restore状态，分如下几种情况：
        #     a.如果没有提交Restore或者Restore已经超时，则不返回该字段。
        #     b.如果已经提交Restore，且Restore没有时完成，则返回的x-oss-restore值为: ongoing-request ="true"。
        #     c.如果已经提交Restore，且Restore已经完成，
        #       则返回的x-oss-restore值为: ongoing-request ="false", expiry-date ="Sun, 16 Apr 2017 08:12:33 GMT"。

        # x-oss-storage-class展示Object的存储类型：Standard，IA，Archive
        storage_class = meta.resp.headers['x-oss-storage-class']
        if storage_class != oss2.BUCKET_STORAGE_CLASS_ARCHIVE:
            return storage_class, restore, finished, expiry_date

        # 状态为restoring的文件，meta中包含信息 'x-oss-restore'为True，
        # 同时也可以从meta.resp.headers中获取： meta.resp.headers['x-oss-restore'] == 'ongoing-request="true"':
        restore_progress = meta.headers.get('x-oss-restore', '')
        if not restore_progress:
            return storage_class, restore, finished, expiry_date
        else:
            restore = True

        if 'true' not in restore_progress:
            # x-oss-restore: ongoing-request="false", expiry-date="Sun, 16 Apr 2017 08:12:33 GMT"
            finished = True
            restore = True
            expiry_time = cls.get_expiry_time(restore_progress)
            expiry_date = timeutil.timestamp_to_date(expiry_time)

        return storage_class, restore, finished, expiry_date

    @classmethod
    def get_expiry_time(cls, restore_progress):
        """Get restore expiry time from restore progress string

        :param restore_progress: e.g. ongoing-request="false", expiry-date="Sun, 16 Apr 2017 08:12:33 GMT"
        :return Unix 时间戳
        """
        expiry_date_str = restore_progress.split(',', 1)[1]
        expiry_date_str = expiry_date_str.replace(' expiry-date="', '').replace('"', '')
        expiry_time = oss2.utils.http_to_unixtime(expiry_date_str)
        return expiry_time


def regulate_part_size(object_size):
    part_size = DEFAULT_SIZE_PER_PART
    while part_size * OSS_MAX_PART_NUM < object_size:
        # part_size 按MB递增
        part_size += part_size
    return part_size


def get_range_size(object_size, byte_range):
    """下载范围: (left, right) 来自oss2注释
        - byte_range 为 (0, 99)  -> 'bytes=0-99'，表示读取前100个字节
        - byte_range 为 (None, 99) -> 'bytes=-99'，表示读取最后99个字节
        - byte_range 为 (100, None) -> 'bytes=100-'，表示读取第101个字节到文件结尾的部分（包含第101个字节）
    """
    if not byte_range:
        return object_size
    left = byte_range[0]
    right = byte_range[1]
    if left == 0 and right > 0:
        return right - left + 1
    elif left is None and right > 0:
        return right
    elif left >= 0 and right is None:
        return object_size - left
    elif 0 <= left < right:
        return right - left + 1
    else:
        raise ValueError("illegal byte range")

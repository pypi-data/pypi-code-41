# -*- coding: utf-8 -*-

"""
FTPStorageDriver：
    * 列出Bucket中的Objects
    * 获取Object的meta信息
    * 文件上传
    * 流式上传
    * 下载到本地文件
    * 流式下载
    * 复制
    * 删除
支持在request中指定``checksum_type``，在传输完成后返回本地计算的校验码结果

1. 关于container name:
                FTP指定一个目录作为容器目录，
                driver的每次操作都会`change work directory`到container目录，
                container 默认为根目录 /

2. 关于object name:
                FTP的object name为container目录下的相对路径，不能以"/"开头：
                container_name: root, ftp路径： /root/a/b/c， object_name: a/c/c

3. 关于list container:
                * prefix为object的上级目录等：
                   例如： a/b/c  -> prefix可以为 a, a/b, a/b/c等，"folder_a/folder_b" 不能写成 "folder_a/fol"
                * 返回的next_marker永远为None，因为ftp server不支持list部分文件，如果想限制返
                回的数量，可以通过iterator_container。
                * iterator和list都是按层遍历，不会递归遍历所有的文件

4. 关于append_file:
                ftp存储中任何已存在或不存在文件，均可以使用append方法追加

5. ftp 返回码： https://en.wikipedia.org/wiki/List_of_FTP_server_return_codes

"""

import ftplib
import functools
import os
import socket
import traceback
import uuid

import gddriver.base as base
import gddriver.errors as gderrors
import gddriver.models as models
import gddriver.utils.io as ioutil
import gddriver.utils.time as timeutil

DEFAULT_CONNECT_TIMEOUT = 30  # 秒, 默认超时时间
DEFAULT_BUFFER_SIZE = 1 << 20  # 1 MB  默认的数据块缓冲大小
DEFAULT_MULTIPART_CHECKSUM_TYPE = 'crc'  # 分片上传时的数据校验方式


def exception_handler(func):

    @functools.wraps(func)
    def ftp_wrapper(*args, **kwargs):
        logger = models.DRIVER_LOGGER_CONFIG.logger
        try:
            return func(*args, **kwargs)
        except (ftplib.error_perm, ftplib.error_reply, ftplib.error_temp) as e:

            logger.warning("ftp driver operation exception occurred. %s",
                           traceback.format_exc())

            status_code, msg = _error_parse(e)
            # 530 Not logged in.
            if int(status_code / 10) == 53:
                raise gderrors.NotLoggedIn(
                    message=msg,
                    status=status_code
                )
            elif status_code == 550:
                raise gderrors.NotFound(message=msg)
            raise gderrors.DriverServerException(msg, status_code)
        except socket.timeout as e:
            logger.warning("ftp socket timeout exception occurred. %s",
                           traceback.format_exc())
            raise gderrors.RequestTimeout(str(e))

    return ftp_wrapper


class FTPConnection(base.Connection):
    """
    FTPConnection 的构造方法中，user对应了基类的access_id, password对应了基类的access_key
    在参数上修改名称是为了便于理解，在内部使用仍然为access_id和access_key
    """

    def __init__(self, host, port, credential, ssl=False, anonymous=False, pasv=False, timeout=None):
        super(FTPConnection, self).__init__(
            host=host,
            port=port,
            credential=credential
        )
        self.ssl = ssl
        self.anonymous = anonymous
        self.pasv = pasv
        self.client = None
        self.timeout = timeout or DEFAULT_CONNECT_TIMEOUT
        self.logger = models.DRIVER_LOGGER_CONFIG.logger

    def clone(self):
        """
            复制一个Connection，避免使用同一个session

              ftp的连接不能够复用，当host、port、用户名密码不变时，不需要重新创建Connection对象，
          直接保留原来的信息复制一个实例
        :return:
        :rtype: :class:`FTPConnection`
        """
        return FTPConnection(
            host=self.host,
            port=self.port,
            credential=self.credential,
            ssl=self.ssl,
            anonymous=self.anonymous,
            pasv=self.pasv
        )

    @exception_handler
    def get_client(self, container_name):
        """
        获取ftp客户端(FTPClient)
        :param container_name: 对于FTP，可指定一个目录作为容器，每次get_client时会进入容器目录
        :return: 如过存在ftp连接未关闭，则会继续复用这个连接
        :rtype: :class:`ftplib.FTP`
        """
        container_root = _get_container_root(container_name)
        if self.client:
            try:
                self.client.cwd(container_root)
                return self.client
            except ftplib.error_temp:
                self.logger.debug(traceback.format_exc())
                # 初次出错，可能连接不可用，忽略问题，尝试重新建立连接
                self.client = None

        user, passwd = (None, None) if self.anonymous else (self.credential.user, self.credential.password)

        if self.ssl:
            ftp_client = self._ssl_connect(user=user, password=passwd)
        else:
            ftp_client = self._normal_connect(user=user, password=passwd)

        try:
            ftp_client.cwd(container_root)
            self.client = ftp_client
            return self.client
        except ftplib.error_perm as e:
            code, msg = _error_parse(e)
            if "change directory" in msg:
                self.logger.warning('ftp change directory failed, %s', traceback.format_exc())
                raise gderrors.NoSuchContainer(container_name)
            else:
                raise

    def _ssl_connect(self, user, password):
        #  ACCT (ACCOUNT)此命令的参数部分使用一个Telnet字符串来指明用户的账户
        ftp = ftplib.FTP_TLS(timeout=self.timeout)
        ftp.set_pasv(self.pasv)
        ftp.connect(self.host, int(self.port))
        # 如果不使用send_cmd的形式登录，抛出异常ftplib.error_perm: 530 Please login with USER and PASS.
        ftp.sendcmd('USER {}'.format(user))
        ftp.sendcmd('PASS {}'.format(password))
        return ftp

    def _normal_connect(self, user, password):
        ftp = ftplib.FTP(timeout=self.timeout)
        ftp.set_pasv(self.pasv)
        ftp.connect(self.host, int(self.port))
        ftp.login(user, password)
        return ftp

    def close(self):
        if self.client:
            try:
                self.client.quit()
            except ftplib.all_errors:
                self.client.close()
            self.client = None


class FTPStorageDriver(base.StorageDriver):

    connection_class = FTPConnection

    def __init__(self):
        super(FTPStorageDriver, self).__init__()

    def list_container_objects(self, connection, container_name, prefix=None, **kwargs):
        """

        返回指定容器内的对象列表

        :param connection:
        :type  connection: :class:`FTPConnection`

        :param container_name: FTP指定一个目录作为容器目录
                                driver的每次操作都会`change work directory`到container目录，
                                container 默认为根目录 /
        :type container_name: :class:`str`

        :param prefix: prefix为object的上级目录等：
                   例如： a/b/c  -> prefix可以为 a, a/b, a/b/c等，"folder_a/folder_b" 不能写成 "folder_a/fol"
        :type  prefix: :class:`str`

        :return: A list of Object instances, next_marker.
        :rtype: ``list`` of :class:`Object` | ``str``

        """
        generator = self.iterate_container_objects(connection, container_name, prefix)
        return [x for x in generator], None

    @exception_handler
    def iterate_container_objects(self, connection, container_name, prefix=None):
        """
        返回指定容器中文件的迭代器

        :param connection:
        :type  connection: :class:`FTPConnection`

        :param container_name: 指定的容器名称.
        :type container_name: :class:`str`

        :param prefix:  5965f2100dd5420091262c06/000000000
        :type  prefix: :class:`str`

        :return: 对象的迭代器
        :rtype: collections.Iterable[Object]
        """
        ftp_client = connection.get_client(container_name)
        container_root = _get_container_root(container_name)
        if prefix:
            _change_work_dir(prefix, ftp_client)
            full_ftp_parent = _normal_full_path(container_root, prefix)
        else:
            full_ftp_parent = container_root
        name_list = ftp_client.nlst()
        for item in name_list:
            is_file, size = _get_file_type_and_size(
                ftp_client=ftp_client,
                name=item,
                sure_exists=True,
                object_name=_join_full_name(prefix, item)
            )
            extra = {
                'parent': full_ftp_parent,
                'short_name': item,
                'is_file': is_file
            }

            prefix = prefix or ''
            obj = models.Object(
                name=_join_full_name(prefix, item),
                size=size,
                **extra
            )
            yield obj

    @exception_handler
    def get_object_meta(self, connection, object_name, container_name):
        """

        :param connection: FTPConnection
        :type connection: :class:`FTPConnection`
        :param object_name: 不包含container目录
        :param container_name: 指定的作为容器的ftp目录
        :return:
        """

        ftp = connection.get_client(container_name)
        container_root = _get_container_root(container_name)
        parent, name = _decomposition_path(object_name)
        full_ftp_path_parent = _normal_full_path(container_root, parent)
        try:
            _change_work_dir(full_ftp_path_parent, ftp)
        except gderrors.NotFound:
            raise gderrors.NoSuchObject(object_name)

        is_file, size = _get_file_type_and_size(
            ftp_client=ftp,
            name=name,
            sure_exists=False,
            object_name=object_name
        )

        extra = {'parent': full_ftp_path_parent, 'is_file': is_file, 'short_name': name}
        return models.Object(
            name=object_name,
            size=size,
            **extra
        )

    @exception_handler
    def download_object_as_stream(self, connection, request):
        """
        FTP流式下载自带了下载的缓冲，默认为64MB。在用户没有及时取出ftp中获取到的数据使用时，下载的数据会存到缓冲区中，
        直到缓冲区满发生阻塞

        :param connection: FTPConnection
        :type connection: :class:`FTPConnection`

        :param request: 流式下载请求
        :type  request: gddriver.models.StreamDownloadRequest

        :return: A generator of file chunk
        :rtype: gddriver.models.StreamDownloadResult
        """
        logger = self.logger
        buffer_size = request.buffer_size
        container_name = request.container_name
        object_name = request.object_name
        progress_callback = request.progress_callback

        obj = self.get_object_meta(connection, object_name, container_name)
        data_size = obj.size

        final_buffer_size = buffer_size
        if not buffer_size or buffer_size < 0:
            final_buffer_size = DEFAULT_BUFFER_SIZE

        stopwatch = timeutil.Stopwatch()
        msg = "download object as stream, container={}, object-key={}, object-size={}, " \
              "buffer-size={}".format(container_name, object_name, obj.size, final_buffer_size)
        logger.info(msg)
        stopwatch.start()

        def generator():
            ftp = connection.get_client(container_name)
            # 通过RETR命令建立下载文件的连接，建立完成后从该连接中获取数据
            conn = ftp.transfercmd('RETR {}'.format(object_name))
            while True:
                try:
                    data = conn.recv(final_buffer_size)
                except Exception:
                    conn.close()
                    raise
                if not data:
                    break
                yield data
            logger.info("%s, elapsed=%s, download finished", msg, stopwatch.elapsed())
            conn.close()

        stream = generator()
        progress_wrapped_stream = ioutil.make_progress_adapter(
            data=stream,
            progress_callback=progress_callback,
            data_size=data_size
        )
        return models.StreamDownloadResult(progress_wrapped_stream, length=data_size)

    @exception_handler
    def download_file(self, connection, request):
        """
        下载文件，对流式下载的封装

        :param connection: FTPConnection
        :type connection: :class:`FTPConnection`

        :param request: 流式下载请求
        :type  request: gddriver.models.FTPDownloadRequest

        """
        logger = self.logger

        container_name = request.container_name
        object_name = request.object_name
        file_path = request.file_path
        progress_callback = request.progress_callback

        if hasattr(request, 'buffer_size'):
            buffer_size = request.buffer_size or DEFAULT_BUFFER_SIZE
        else:
            buffer_size = DEFAULT_BUFFER_SIZE

        stream_download_request = models.FTPStreamDownloadRequest(
            container_name=container_name,
            object_name=object_name
        )
        stream_download_request.container_name = container_name
        stream_download_request.object_name = object_name
        stream_download_request.progress_callback = progress_callback
        stream_download_request.buffer_size = buffer_size

        generator = self.download_object_as_stream(
            connection=connection,
            request=stream_download_request
        )

        msg = "download to file, bucket={}, object-key={}, " \
              "dst-path={}, buffer-size={}".format(container_name, object_name, file_path, buffer_size)

        logger.debug(msg)
        with open(file_path, 'wb') as f:
            for data in generator:
                f.write(data)

    @exception_handler
    def upload_object_via_stream(self, connection, request):
        """
        流式上传，可以上传网络流、文件流、字符串、bytes等可迭代的对象。

        :param connection: FTPConnection
        :type connection: :class:`FTPConnection`

        :param request:
        :type  request: `gddriver.models.FTPStreamUploadRequest`

        :rtype: ``gddriver.models.UploadResult``
        """
        logger = self.logger

        container_name = request.container_name
        object_name = request.object_name
        stream = request.stream
        progress_callback = request.progress_callback
        checksum_type = request.checksum_type
        data_size = request.data_size

        logger.debug("Upload object %s via stream", object_name)
        upload_chunk_size = int(DEFAULT_BUFFER_SIZE / 2)
        checksum, checksum_type = self.__upload_via_stream(
            cmd='STOR',
            connection=connection,
            object_name=object_name,
            stream=stream,
            container_name=container_name,
            checksum_type=checksum_type,
            chunk_size=upload_chunk_size,
            progress_callback=progress_callback,
            data_size=data_size,
            logger=logger
        )

        return models.UploadResult(
            checksum_type=checksum_type,
            checksum=checksum
        )

    @exception_handler
    def upload_file(self, connection, request):
        """
        上传文件到FTP中

        :param connection:
        :type  connection: :class:`FTPConnection`

        :param request:
        :type  request: `gddriver.models.FTPUploadRequest`

        :rtype: ``UploadResult``
        """
        logger = self.logger

        container_name = request.container_name
        file_path = request.file_path
        object_name = request.object_name
        progress_callback = request.progress_callback
        checksum_type = request.checksum_type

        if hasattr(request, 'buffer_size'):
            buffer_size = request.buffer_size or DEFAULT_BUFFER_SIZE
        else:
            buffer_size = DEFAULT_BUFFER_SIZE

        logger.debug("Upload file %s to %s/%s", file_path, container_name, object_name)

        with open(file_path, 'rb') as f:
            checksum, checksum_type = self.__upload_via_stream(
                cmd='STOR',
                connection=connection,
                object_name=object_name,
                stream=f,
                container_name=container_name,
                checksum_type=checksum_type,
                progress_callback=progress_callback,
                chunk_size=buffer_size,
                logger=logger
            )
            return models.UploadResult(
                checksum=checksum,
                checksum_type=checksum_type
            )

    @exception_handler
    def append_object(self, connection, request):
        """
        追加上传文件，FTP对追加文件没有限制，已存在的任何文件都可以以二进制的形式追加上传，但是只能从文件
        尾部开始追加

        :param connection: FTPConnection
        :type connection: :class:`FTPConnection`

        :param request:
        :type  request: `gddriver.models.AppendRequest`

        :rtype: ``AppendResult``
        """
        logger = self.logger

        container_name = request.container_name
        object_name = request.object_name
        stream = request.stream
        progress_callback = request.progress_callback
        position = request.position
        checksum_type = request.checksum_type
        data_size = request.data_size

        logger.debug("Append object %s via stream", object_name)

        try:
            obj = self.get_object_meta(connection, object_name, container_name)
        except gderrors.NoSuchObject:
            obj = None
            logger.info("Append object %s via stream, no such object", object_name)

        if obj and position != obj.size:
            raise gderrors.AppendPositionConflict(position)

        checksum, checksum_type = self.__upload_via_stream(
            cmd='APPE',
            connection=connection,
            object_name=object_name,
            stream=stream,
            container_name=container_name,
            checksum_type=checksum_type,
            progress_callback=progress_callback,
            data_size=data_size,
            logger=logger
        )

        obj = self.get_object_meta(connection, object_name, container_name)
        return models.AppendResult(
            next_position=obj.size,
            checksum_type=checksum_type,
            checksum=checksum
        )

    @exception_handler
    def delete_object(self, connection, object_name, container_name=None):
        """
        删除文件，文件不存在时会抛出异常
        :param connection: FTPConnection
        :type connection: :class:`FTPConnection`

        :param object_name: 不包含container名称
        :type object_name: :class:`str`

        :param container_name: 指定的作为容器的ftp目录
        :type container_name: :class:`str`

        """

        ftp = connection.get_client(container_name)
        ftp.delete(object_name)

    @exception_handler
    def copy_object(self, connection, request):
        """

        :param connection:
        :type  connection: :class:`FTPConnection`
        :param request: 对象复制请求
        :type  request: :class:``gddriver.models.CopyRequest``
        :return:
        """
        logger = self.logger

        src_container_name = request.container_name
        src_object_name = request.object_name
        # 默认复制到当前容器中
        dst_container_name = request.dst_container_name or src_container_name
        dst_object_name = request.dst_object_name

        msg = "copy object from {}/{} to {}/{}".format(src_container_name, src_object_name,
                                                       dst_container_name, dst_object_name)
        logger.debug(msg)
        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        stream_download_request = models.FTPStreamDownloadRequest(
            container_name=src_container_name,
            object_name=src_object_name
        )
        stream_download_request.buffer_size = DEFAULT_BUFFER_SIZE
        stream = self.download_object_as_stream(
            connection=connection,
            request=stream_download_request
        )

        stream_upload_request = models.FTPStreamUploadRequest(
            container_name=dst_container_name,
            stream=stream,
            object_name=dst_object_name
        )

        stream_upload_request.checksum_type = 'md5'
        # 必须复制一个连接，否则会阻塞
        copy_connection = connection.clone()
        try:
            res = self.upload_object_via_stream(
                connection=copy_connection,
                request=stream_upload_request
            )

            logger.debug("%s, res: %s, elapsed=%s, copy finished", msg, res, stopwatch.elapsed())

        finally:
            copy_connection.close()

    def restore_object(self, connection, src_container_name, src_object_name, **kwargs):
        raise NotImplementedError

    def archive_object(self, connection, src_container_name, src_object_name, archive_container_name,
                       archive_object_name,
                       **kwargs):
        raise NotImplementedError

    @exception_handler
    def move_object(self, connection, src_object_name, dst_object_name, container_name=None, dst_container_name=None):
        """
        重命名： src_container/src_obj -> dst_container/dst_obj
        NOTE: raise 250异常时，多是因为复用ftp_client造成，使用connection.clone复制一个连接可避免该问题

        :param connection:
        :type  connection: :class:`Connection`

        :param src_object_name: 原始对象名
        :type src_object_name: `str`

        :param dst_object_name: 目标对象名称
        :type dst_object_name: `str`

        :param container_name: 原文件所在的容器 （默认为ftp存储的根目录 "/" ）
        :type  container_name: :class:`str`

        :param dst_container_name: 目标容器（默认原文件所在容器）
        :type dst_container_name: `str`

        """
        msg = "move object from {}/{} to {}/{}".format(container_name, src_object_name,
                                                       dst_container_name, dst_object_name)
        self.logger.debug(msg)
        ftp_client = connection.get_client(container_name)

        def build_prefix(name):
            return '/' + name if name else '/'

        prefix_src = build_prefix(container_name)
        prefix_dst = build_prefix(dst_container_name) if dst_container_name else prefix_src
        src_path = '/'.join([prefix_src, src_object_name])
        dst_path = '/'.join([prefix_dst, dst_object_name])
        res = ftp_client.rename(src_path, dst_path)
        self.logger.info(res)

    @exception_handler
    def init_multipart_upload(self, connection, object_name, container_name=None, overwrite=False):
        """
        初始化分片上传 （ftp服务中创建 object_name.multi-uuid 目录用于分片上传缓存）
        :type connection: FTPConnection
        :type object_name: str
        :type container_name: str
        :param overwrite: 覆盖原文件
        :rtype: str
        """

        upload_id = "multi-{}".format(uuid.uuid1())
        if overwrite:
            try:
                self.delete_object(
                    connection=connection,
                    object_name=object_name,
                    container_name=container_name
                )
            except gderrors.NotFound as e:
                self.logger.debug("file not found while initializing multi-upload and overwrite %s: %s", object_name, e)
        multi_tmp_dir = self.__get_multi_tmp_dir_with_check(
            connection=connection,
            container_name=container_name,
            object_name=object_name,
            upload_id=upload_id,
            init=True
        )

        # create tmp dir
        self.check_or_make_dir(
            connection=connection,
            container_name=container_name,
            path=multi_tmp_dir
        )
        self.logger.debug("multipart upload tmp directory %s created", multi_tmp_dir)

        return upload_id

    @exception_handler
    def upload_part(self, connection, request):
        """
        分片上传，上传时默认计算分片的crc校验码并作为ETag返回（合并分片时通过ETag中的校验码对分片进行校验）

        :type connection: FTPConnection
        :type request: gddriver.models.PartUploadRequest
        :return:
        """
        multi_tmp_dir = self.__get_multi_tmp_dir_with_check(
            connection=connection,
            container_name=request.container_name,
            object_name=request.object_name,
            upload_id=request.upload_id
        )

        part_name = '/'.join([multi_tmp_dir, str(request.part_number)])
        stream_upload_request = models.FTPStreamUploadRequest(
            container_name=request.container_name,
            stream=request.stream,
            object_name=part_name
        )
        stream_upload_request.progress_callback = request.progress_callback
        stream_upload_request.checksum_type = DEFAULT_MULTIPART_CHECKSUM_TYPE
        result = self.upload_object_via_stream(
            connection=connection,
            request=stream_upload_request
        )

        # etag统一为string
        part_etag = self.__checksum_to_etag(result.checksum)
        return models.PartUploadResult(
            checksum_type=result.checksum_type,
            checksum=result.checksum,
            part_info=models.PartInfo(etag=part_etag, part_number=request.part_number)
        )

    @exception_handler
    def complete_multipart_upload(self, connection, request):
        """ 合并所有分块，当目标文件已存在时或分块文件不存在时抛出异常
        throws:
            FileAlreadyExists  object_name对应的文件已存在
            BadRequest  upload_id对应的临时目录不存在或分片参数有问题

        :type connection: FTPConnection
        :type request: gddriver.models.CompleteMultipartUploadRequest
        """

        multi_tmp_dir = self.__get_multi_tmp_dir_with_check(
            connection=connection,
            container_name=request.container_name,
            object_name=request.object_name,
            upload_id=request.upload_id
        )

        parts = models.PartInfo.sort_parts(request.parts)
        tmp_name = '/'.join([multi_tmp_dir, "tmp"])

        def _merge_parts():
            """按照分片的顺序将各个分片文件append到同一个文件中"""
            position = 0
            for part in parts:
                part_name = '/'.join([multi_tmp_dir, str(part.part_number)])
                stream_download_request = models.FTPStreamDownloadRequest(
                    container_name=request.container_name,
                    object_name=part_name
                )
                stream_download_request.buffer_size = DEFAULT_BUFFER_SIZE

                try:
                    part_stream = self.download_object_as_stream(connection, stream_download_request)
                except gderrors.NotFound as _e:
                    raise gderrors.BadRequest("One or more of the specified parts could not be found: {}".format(_e))

                conn_clone = connection.clone()
                with conn_clone:
                    append_request = models.AppendRequest(
                        container_name=request.container_name,
                        object_name=tmp_name,
                        stream=part_stream,
                        position=position
                    )
                    append_request.checksum_type = DEFAULT_MULTIPART_CHECKSUM_TYPE
                    append_result = self.append_object(
                        connection=conn_clone,
                        request=append_request
                    )
                    if self.__checksum_to_etag(append_result.checksum) != part.etag:
                        raise gderrors.BadRequest(("The specified entity tag not matched "
                                                   "the part's entity tag, request: {}, actually: {}").format(
                            part.etag, append_result.checksum
                        ))
                position += part_stream.__len__()

        stopwatch = timeutil.Stopwatch()
        stopwatch.start()
        self.logger.debug("start complete multipart upload %s, parts=%s, upload_id=%s, time-elapsed=%s",
                          request.object_name, len(request.parts), request.upload_id)
        copy_conn = connection.clone()
        with copy_conn:
            try:
                # 合并分片到一个临时文件
                _merge_parts()

                # rename tmp -> object_name
                self.move_object(copy_conn, tmp_name, request.object_name, container_name=request.container_name)

                # 删除临时目录
                self.delete_dir(
                    container_name=request.container_name,
                    connection=copy_conn,
                    dir_name=multi_tmp_dir
                )
            finally:
                self.logger.debug("finished complete multipart upload %s, parts=%s, upload_id=%s, time-elapsed=%s",
                                  request.object_name, len(request.parts), request.upload_id, stopwatch.elapsed())
                # 失败时删除临时文件
                try:
                    self.delete_object(
                        connection=copy_conn,
                        container_name=request.container_name,
                        object_name=tmp_name
                    )
                except gderrors.NotFound:
                    pass
                except gderrors.DriverServerException as e:
                    self.logger.debug("An exception occurred during delete %s: %s", tmp_name, e)

    def batch_delete_objects(self, connection, object_name_list, container_name=None):
        raise NotImplementedError

    def get_object_sign_url(self, connection, object_name, container_name=None, **kwargs):
        raise NotImplementedError

    def __get_multi_tmp_dir_with_check(self, connection, container_name, object_name, upload_id, init=False):
        """获取分片上传的临时目录，并同时检查upload_id是否有效"""
        try:
            meta = self.get_object_meta(
                container_name=container_name,
                connection=connection,
                object_name=object_name
            )
            if meta:
                raise gderrors.FileAlreadyExists("File {} already exists".format(meta))
        except gderrors.NotFound:
            pass

        multi_tmp_dir = self.__multi_tmp_dir(object_name, upload_id)
        if not init:
            try:
                dir_meta = self.get_object_meta(
                    connection=connection,
                    container_name=container_name,
                    object_name=multi_tmp_dir
                )
                self.logger.debug("Found multipart upload process: {}".format(dir_meta))
            except gderrors.NotFound as e:
                self.logger.warning("Not found such upload_id: %s", e)
                raise gderrors.BadRequest("Not found such upload_id {} with object {}".format(
                    upload_id, object_name))
        return multi_tmp_dir

    @staticmethod
    def __checksum_to_etag(checksum):
        """将crc/md5转为etag，当前默认转为str类型"""
        return str(checksum)

    @staticmethod
    def __multi_tmp_dir(object_name, upload_id):
        """
        format: object_name.multi-uuid

        :param str object_name: file path
        :param str upload_id: multipart upload id
        :rtype: str
        """
        return '.'.join([object_name, upload_id])

    @classmethod
    def __upload_via_stream(cls, cmd, connection, stream, container_name, object_name, checksum_type=None,
                            progress_callback=None, data_size=None, logger=None, chunk_size=None):

        parent, name = _decomposition_path(object_name)
        cls.check_or_make_dir(
            connection=connection,
            container_name=container_name,
            path=parent
        )

        ftp_client = connection.get_client(container_name)
        _change_work_dir(parent, ftp_client)

        progress_wrapped_stream = ioutil.make_progress_adapter(
            data=stream,
            progress_callback=progress_callback,
            data_size=data_size
        )
        checksum_wrapped_stream = ioutil.make_checksum_adapter(
            progress_wrapped_stream,
            checksum_type=checksum_type
        )

        readable_stream = ioutil.make_file_like_adapter(checksum_wrapped_stream)

        # 开始传输
        msg = "upload via stream, container={}, object-key={}, checksum-type={}, " \
              "data-size={}".format(container_name, object_name, checksum_type, data_size)
        logger.info(msg)
        stopwatch = timeutil.Stopwatch()
        stopwatch.start()

        # stirbinary: ftp 上传操作，其中包括 STOR(存储), APPE(追加) 等命令
        ftp_client.storbinary(
            cmd='{} {}'.format(cmd, name),
            fp=readable_stream,
            blocksize=chunk_size
        )

        logger.info('%s, checksum=%s, elapsed=%s, upload finished',
                    msg, checksum_wrapped_stream.checksum, stopwatch.elapsed())

        return checksum_wrapped_stream.checksum, checksum_wrapped_stream.checksum_type

    @classmethod
    def check_or_make_dir(cls, connection, container_name, path):
        """
        递归创建目录
        :type  connection: :class:`FTPConnection`
        :type  container_name: :class:`str`
        :type  path: :class:`str`
        """
        if not path:
            return
        container_root = _get_container_root(container_name)
        ftp = connection.get_client(container_name)
        try:
            ftp.cwd(path)
        except ftplib.error_perm:
            parent, name = _decomposition_path(path)
            cls.check_or_make_dir(connection, container_name, parent)
            full_parent_path = _normal_full_path(container_root, parent)
            ftp.cwd(full_parent_path)
            ftp.mkd(name)

    @classmethod
    @exception_handler
    def delete_dir(cls, connection, container_name, dir_name):
        """
        递归删除目录
        :type  connection: :class:`FTPConnection`
        :type container_name: :class:`str`
        :type  dir_name: :class:`str`
        """
        ftp = connection.get_client(container_name)
        name_list = ftp.nlst(dir_name)
        if name_list:
            for name in name_list:
                try:
                    ftp.size(name)
                    ftp.delete(name)
                except ftplib.error_perm:
                    cls.delete_dir(connection, container_name, name)
        ftp.rmd(dir_name)


def _error_parse(err):
    """
    错误实例：
        530	Not logged in.
    :param err:
    :type :class:`ftplib.Error`
    :return:
    """
    msg_str = str(err)
    if len(msg_str) < 3:
        return None, msg_str

    code = msg_str[:3]
    msg = msg_str[3:]
    try:
        code = int(code)
    except ValueError:
        code = None
        msg = msg_str
    return code, msg


def _change_work_dir(directory, ftp_client):
    if directory == '':
        return

    logger = models.DRIVER_LOGGER_CONFIG.logger
    try:
        logger.info('try to change directory to %s.', directory)
        ftp_client.cwd(directory)
        logger.info('current directory changed: %s.', directory)
    except ftplib.error_perm as e:
        status, msg = _error_parse(e)
        # 550 Requested action not taken. File unavailable (e.g., file not found, no access).
        if status == 550:
            raise gderrors.NotFound(
                status=550,
                message="directory not found: {}".format(directory)
            )
        raise


def _decomposition_path(path):
    """ /a/b/c/d -> (a/b/c, d)"""

    if not path:
        return '', ''
    path = os.path.normpath(path)
    sp = path.split('/')

    parent = ''
    name = sp[-1]
    if len(sp) > 1:
        parent = os.path.normpath('/'.join(sp[:-1]))
    return parent, name


def _get_container_root(container_name=None):
    """ /container_name/ """
    return '/{}/'.format(container_name) if container_name else '/'


def _normal_full_path(container_root, path):
    """ /container_name/path/
    :param container_root:  /container_name/
    :param path:            path
    :return 拼接的路径，统一以 '/' 结尾
    """
    full_path = container_root + path
    full_path = os.path.normpath(full_path)
    return full_path + '/' if full_path != '/' else full_path


def _join_full_name(prefix, name):
    if not prefix:
        return name
    if not prefix.endswith('/'):
        return '/'.join([prefix, name])
    else:
        return ''.join([prefix, name])


def _get_file_type_and_size(ftp_client, name, sure_exists=True, object_name=None):
    """ (is_file, file_size)"""
    logger = models.DRIVER_LOGGER_CONFIG.logger
    try:
        logger.info('try to get the size of %s. (object_name: %s)', name, object_name)
        size = ftp_client.size(name)
        if size is None:
            # FTP lib的bug，有时跟在cwd命令后的命令会无任何返回值，尝试再次获取文件大小
            size = ftp_client.size(name)
        if size is None:
            raise gderrors.DriverServerException("get size failed")
        logger.info('get the size of %s finished. (object_name: %s)', name, object_name)
        return True, size
    except ftplib.error_perm as e:
        status, msg = _error_parse(e)
        if status != 550:
            raise
        size = 0
        is_file = False
        if not sure_exists:
            try:
                # 通过切换目录检查目录是否存在
                pwd = ftp_client.pwd()
                _change_work_dir(name, ftp_client)
                _change_work_dir(pwd, ftp_client)
            except gderrors.NotFound:
                raise gderrors.NoSuchObject(object_name)
        return is_file, size

# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import collections
import hashlib
import os
import threading
import struct

import crcmod

import gddriver.utils as utils
import gddriver.errors as gderrors

Iterable = collections.Iterable
_CHUNK_SIZE = 1024 * 100


"""
str_type： 不可直接作为bytes使用的类型，进行md5、crc等计算前需要encode操作

对于PY2：str 等价于 bytes，不需要编码操作
对于PY3：str 不同于 bytes，需要显式地编码操作
"""
if utils.PY2:
    str_type = (unicode,)  # py2 - unicode: unencoded，builtin str: encoded
else:
    str_type = (str,)  # py3 - builtin str: unencoded


def make_checksum_adapter(data, checksum_type='crc'):
    """为data添加checksum/checksum_type属性"""
    if hasattr(data, 'read'):
        return _FileLikeAdapter(data, checksum_type=checksum_type)
    elif isinstance(data, Iterable):
        return _IterableAdapter(data, checksum_type=checksum_type)
    else:
        raise gderrors.DataAdapterWrapException(data)


def make_progress_adapter(data, progress_callback, data_size=None):
    """为data添加进度回调"""

    if hasattr(data, 'read'):
        return _FileLikeAdapter(data, progress_callback=progress_callback, data_size=data_size)
    elif isinstance(data, Iterable):
        return _IterableAdapter(data, progress_callback=progress_callback, data_size=data_size)
    else:
        raise gderrors.DataAdapterWrapException(data)


def make_file_like_adapter(data):
    """将普通的iterator转换为FileLike对象（增加read操作）"""
    if hasattr(data, 'read'):
        return data
    elif isinstance(data, Iterable):
        return _IteratorToFileAdapter(data)
    else:
        raise gderrors.DataAdapterWrapException(data)


def make_file_iterator(file_path, chunk_size=8092):
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


class Adapter(object):
    """progress_callback/checksum 适配器，为对象添加progress_callback功能/checksum属性"""
    def __init__(self, progress_callback=None, checksum_type=None, data_size=None, **kwargs):

        self.progress_callback = progress_callback
        self._data_size = data_size
        self._checksum_callback = None
        self.__checksum_type = checksum_type
        if checksum_type:
            if checksum_type.lower() == 'crc':
                self._checksum_callback = Crc64()
            elif checksum_type.lower() == 'md5':
                self._checksum_callback = MD5()

    @property
    def checksum(self):
        if not self._checksum_callback:
            return None
        return self._checksum_callback.checksum

    @property
    def checksum_type(self):
        return self.__checksum_type


class _FileLikeAdapter(Adapter):
    """
    checksum/progress_callback适配器，包装带有'read'方法的可迭代类型，
    为其添加progress_callback功能/checksum属性
    """

    def __init__(self, data, progress_callback=None, checksum_type=None, data_size=None):
        super(_FileLikeAdapter, self).__init__(progress_callback, checksum_type, data_size)

        # encode to bytes (utf-8)
        self.file_data = str_to_bytes(data)
        self._data_size = data_size or _get_data_size(data)
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        content = self.read(_CHUNK_SIZE)

        if content:
            return content
        else:
            raise StopIteration

    def read(self, amt=None):
        content = self.file_data.read(amt)
        if not content:
            _progress_callback(self.progress_callback, self.offset, self._data_size)
        else:
            _progress_callback(self.progress_callback, self.offset, self._data_size)

            self.offset += len(content)

            _checksum_callback(self._checksum_callback, content)
        return content


class _IterableAdapter(Adapter):
    """
     checksum/progress_callback适配器，包装普通的可迭代类型，
    为其添加progress_callback功能/checksum属性
    """
    def __init__(self, data, progress_callback=None, checksum_type=None, data_size=None):
        super(_IterableAdapter, self).__init__(progress_callback, checksum_type, data_size)

        # encode to bytes (utf-8)
        encoded_data = str_to_bytes(data)
        if type(data) == bytes or type(data) == str:
            # bytes to iterator
            self.iter = iter([encoded_data])
        else:
            self.iter = iter(encoded_data)
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        _progress_callback(self.progress_callback, self.offset, self._data_size)

        content = next(self.iter)
        self.offset += len(content)

        _checksum_callback(self._checksum_callback, content)

        return content


class _IteratorToFileAdapter(object):
    """
    FileLike适配器，将普通的iterator转换为FileLike对象
    """
    def __init__(self, iterator):
        self.iter = iterator
        self.remain = None
        self.offset = 0

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):

        content = self.read(_CHUNK_SIZE)

        if content:
            return content
        else:
            raise StopIteration

    def read(self, amt=None):
        amt = int(amt or 0)
        content = self._read_with_amt(amt) if amt else self._read_without_amt()
        if content:
            self.offset += len(content)
        return content

    def _read_without_amt(self):
        content = b''
        content += self.remain or b''
        self.remain = None
        while True:
            try:
                data = unpack_to_bytes(next(self.iter))
                content += data
            except StopIteration:
                break
        return content

    def _read_with_amt(self, amt):
        content = b''
        if self.remain:
            buf = min(amt, len(self.remain))
            content = self.remain[:buf]
            self.remain = self.remain[buf:]

        while not content or len(content) < amt:
            need = amt - len(content)
            try:
                self.remain = unpack_to_bytes(next(self.iter))
            except StopIteration:
                break
            content += self.remain[:need]
            self.remain = self.remain[need:]
        return content


def _progress_callback(function, offset, data_size):
    if function:
        function(offset, data_size)


def _checksum_callback(checksum_callback, content):
    if checksum_callback:
        checksum_callback(content)


def _get_data_size(data):
    if hasattr(data, '__len__'):
        return len(data)

    if hasattr(data, 'seek') and hasattr(data, 'tell'):
        return file_object_remaining_bytes(data)

    return None


def file_object_remaining_bytes(fileobj):
    current = fileobj.tell()

    fileobj.seek(0, os.SEEK_END)
    end = fileobj.tell()
    fileobj.seek(current, os.SEEK_SET)

    return end - current


class Crc64(object):
    """
    使用与oss相同的生成多项式(ECMA-182标准)计算crc64
    """
    _POLY = 0x142F0E1EBA9EA3693
    _XOROUT = 0xFFFFFFFFFFFFFFFF

    def __init__(self, init_crc=0):
        self.crc64 = crcmod.Crc(self._POLY, initCrc=init_crc, rev=True, xorOut=self._XOROUT)

    def __call__(self, data):
        self.update(data)

    def update(self, data):
        self.crc64.update(data)

    @property
    def checksum(self):
        return self.crc64.crcValue


class MD5(object):

    def __init__(self):
        self.md5 = hashlib.md5()

    def __call__(self, data):
        self.update(data)

    def update(self, data):
        self.md5.update(data)

    @property
    def checksum(self):
        return self.md5.hexdigest()


def copy_file(stream, dst):
    size = 0
    for chunk in stream:
        dst.write(chunk)
        size += len(chunk)
    return size


def create_checksum_yield(file_path, checksum_type, logger=None):
    f = open(file_path, 'rb')
    adapter = make_checksum_adapter(f, checksum_type)

    def calculate():
        if logger:
            logger.debug("DriverAction=checksum, file_path={}".format(file_path))
        try:
            if not checksum_type:
                return
            for ignored in adapter:
                pass
        finally:
            f.close()

    task = threading.Thread(target=calculate, args=())
    task.start()

    def generator():
        task.join()
        yield adapter.checksum

    return generator()


def str_to_bytes(data):
    """若输入为str（unicode），则转为utf-8编码的bytes；其他则原样返回"""
    if isinstance(data, str_type):
        return data.encode(encoding='utf-8')
    else:
        return data


def unpack_to_bytes(data):
    """
    将迭代器中获取的内容转换为bytes内容:
        str -> bytes
        int -> bytes
    :param data: str/bytes/int
    :return: bytes
    """

    content = str_to_bytes(data)

    if isinstance(content, int):
        return struct.pack('B', content)
    return content

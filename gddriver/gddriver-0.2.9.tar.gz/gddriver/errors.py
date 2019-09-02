# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals


class StorageDriverException(Exception):
    message = "Storage driver operation exception."

    def __init__(self, message=None, **kwargs):
        self.message = message or self.message
        self.details = {}
        self.details.update(**kwargs)

    def __str__(self):
        return "{}  details: {}".format(self.message, self.details or None)


class DriverLocalException(StorageDriverException):
    message = "Storage driver local operation exception."


class DriverRequestException(StorageDriverException):
    message = "Storage driver request operation exception."


class DriverServerException(StorageDriverException):
    message = "Storage driver server process exception."
    status = 500

    def __init__(self, message=None, status=None, **kwargs):
        super(DriverServerException, self).__init__(message, **kwargs)
        self.status = status or self.status

    def __str__(self):
        return '{} {}'.format(self.status, super(DriverServerException, self).__str__())


class RequestTimeout(DriverRequestException):
    message = "Request timeout"


class IllegalParameter(DriverLocalException):
    message = "Illegal parameter"

    def __init__(self, name=None, value=None):
        if name:
            self.message += ", " + name
        if value:
            self.message = "{}: {}".format(self.message, value)
        super(IllegalParameter, self).__init__(self.message)


class DataAdapterWrapException(DriverLocalException):

    def __init__(self, data):
        self.message = '{0} is not a file object, nor an iterator'.format(data.__class__.__name__)
        super(DataAdapterWrapException, self).__init__(self.message)


class FileAlreadyExists(DriverLocalException):
    message = "File already exists"

    def __init__(self, msg):
        super(FileAlreadyExists, self).__init__(msg)


class PathTypeConflict(DriverLocalException):
    message = "Path conflict."


class TransferError(DriverLocalException):
    message = "Transfer error."


class UnexpectedDownloadedSize(TransferError):
    def __init__(self, expect_size, actual_size):
        self.message = "Unexpected downloaded file size: expect: {}, actual: {}".format(expect_size, actual_size)
        super(UnexpectedDownloadedSize, self).__init__(self.message)


class GetConnectException(DriverLocalException):
    message = "Get connect exception, miss parameters."


class BadRequest(DriverServerException):
    status = 400


class OperationNotSupported(BadRequest):
    message = "Operation not supported"


class Forbidden(DriverServerException):
    status = 403
    message = "Forbidden"


class NotLoggedIn(Forbidden):
    pass


class NotFound(DriverServerException):
    status = 404
    message = "Not found"


class NoSuchObject(NotFound):
    def __init__(self, object_name, **kwargs):
        self.message = "No such object: {}".format(object_name)
        super(NoSuchObject, self).__init__(**kwargs)


class NoSuchContainer(NotFound):
    def __init__(self, container_name, **kwargs):
        self.message = "No such container: {}".format(container_name)
        super(NoSuchContainer, self).__init__(**kwargs)


class Conflict(DriverServerException):
    status = 409
    message = 'conflict'


class AppendPositionConflict(Conflict):
    def __init__(self, position, **kwargs):
        self.message = "Position is not equal to remote file length {}".format(position)
        super(AppendPositionConflict, self).__init__(**kwargs)


class ChecksumMismatch(Conflict):
    def __init__(self, message, server_checksum, client_checksum, **kwargs):
        self.message = "{}, checksum mismatch: server checksum: {}, client checksum: {}".format(
            message, server_checksum, client_checksum
        )
        super(ChecksumMismatch, self).__init__(**kwargs)

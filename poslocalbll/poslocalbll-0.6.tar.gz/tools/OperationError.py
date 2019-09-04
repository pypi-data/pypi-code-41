# -*- coding: utf-8 -*-
from loggingm import logger


class OperationError(Exception):
    def __init__(self, code, message, inner_exception=None, *, response_status=200):
        Exception.__init__(self, message, {"message": message, "code": code, "inner_exception": inner_exception})
        self.inner_exception = inner_exception
        self.message = message
        self.code = code
        self.response_status = response_status
        logger.error(str(message))

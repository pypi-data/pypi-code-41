from rdsr_navigator.sr_exceptions.sr_exception_base import SrExceptionBase

class SrMissingContentException(SrExceptionBase):
    def __init__(self, message=''):
        super().__init__(message)

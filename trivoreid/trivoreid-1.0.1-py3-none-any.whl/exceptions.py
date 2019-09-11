#!/usr/bin/env python
# coding: utf-8

class TrivoreIDSDKException(Exception):
    '''
    An Exception raised when TrivoreID SDK is not properly used.
    '''

    @property
    def message(self):
        return self.__dict__.get('message', None) or getattr(self, 'args')[0]

class TrivoreIDException(Exception):
    '''
    An Exception occured in TrivoreID.
    Args:
        message (str) : error message
        code : server response code
    '''

    def __init__(self, message, code = None):
        self.resporse_code = code
        super().__init__(message)

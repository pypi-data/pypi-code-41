# -*-
#
# @author: jaumebonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.github.io
#
# @date:   2016-02-16 10:41:23
#
# @last modified by:   jaumebonet
# @last modified time: 2016-02-16 18:07:21
#
# -*-
from abc import abstractmethod
from pynion import Singleton


class Parser(object):
    """:py:class:`Parser <SBI.structure.parsers.Parser>` is the main class from
    which all the rest should derive. It forces the declaration of the read and
    write functions in all parsers.
    """
    __metaclass__ = Singleton

    def __init__(self):
        pass

    @abstractmethod
    def read(self, file_name):
        raise NotImplementedError

    @abstractmethod
    def write(self, json_object, file_name):
        raise NotImplementedError



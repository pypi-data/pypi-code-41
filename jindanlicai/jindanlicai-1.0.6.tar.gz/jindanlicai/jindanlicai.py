# encoding: UTF-8
import json
import uuid, time
import hashlib
import logging
import robot
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn
import base64
import rncryptor
from jsonpath_rw_ext import parse
import sys

from RequestsLibrary import RequestsLibrary

PY3 = sys.version_info > (3,)

class JindanlicaiKeyWords(object):
    ROBOT_LIBRARY_SCOPE = 'Global'

    def __init__(self):
        self.requests_lib = RequestsLibrary()
        self.builtin = BuiltIn()
        self.debug = 0
    def get_uuid(self,name):
        return str(name)

    def get_uuid_noline(self):
        return str(uuid.uuid1()).replace('-', '')
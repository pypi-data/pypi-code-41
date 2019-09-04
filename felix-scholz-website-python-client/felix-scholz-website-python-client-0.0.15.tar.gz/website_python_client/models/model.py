# coding: utf-8

"""
    Felix' Website mit Blog

    The api of my blog.


    Contact: felix@felix-scholz.org
    Date: 17. Jul 2019
"""
import hashlib
import mimetypes
import os
import re
from typing import Tuple, List, Union

from datetime import datetime

from website_python_client.api.rest_response import RESTResponse


class Model(object):
    def __init__(self):
        pass

    def deserialize(self, data: RESTResponse) -> 'Model':
        pass

    @staticmethod
    def deserialize_all(data: RESTResponse) -> List['Model']:
        pass

    @staticmethod
    def hash_identifier(hash_str: Union[str, bytes] = '') -> str:
        """

        :param str hash_str:
        :return str:
        """
        m = hashlib.sha512()
        m.update(hash_str.encode('utf-8'))

        return m.hexdigest()

    @staticmethod
    def upload_file(file: Tuple[str, str]) -> Tuple[str, Tuple[str, bytes, str]]:
        """Builds form parameters.

        :param file: File parameters.
        :return: Form parameters with files.
        """
        parameter, file_path = file

        with open(file_path, 'rb') as f:
            filename = os.path.basename(f.name)
            mime_type = (mimetypes.guess_type(filename)[0] or 'application/octet-stream')

            return parameter, (filename, f.read(), mime_type)

    @staticmethod
    def datetime(_datetime: str) -> datetime:
        matches = re.match(
            r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hour>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})',
            _datetime
        )

        return datetime(
            int(matches.group('year')), int(matches.group('month')), int(matches.group('day')),
            int(matches.group('hour')), int(matches.group('minutes')), int(matches.group('seconds')), 0)


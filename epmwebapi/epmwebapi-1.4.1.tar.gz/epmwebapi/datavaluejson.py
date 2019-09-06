"""
Elipse Plant Manager - EPM Web API
Copyright (C) 2018 Elipse Software.
Distributed under the MIT License.
(See accompanying file LICENSE.txt or copy at http://opensource.org/licenses/MIT)
"""

import dateutil
import datetime
from datetime import timezone

class DataValueJSON(object):
    """description of class"""
    def __init__(self, value, statusCode, timestamp):
        self._value = value
        self._statusCode = statusCode
        if type(timestamp) == str:
          self._timestamp = dateutil.parser.parse(timestamp).astimezone(timezone.utc)
        else:
          self._timestamp = timestamp

    @property
    def value(self):
      return self._value

    @property
    def statusCode(self):
      return self._statusCode

    @property
    def timestamp(self):
      return self._timestamp

    def toDict(self):
        return {'value': self._value, 'quality': self._statusCode, 
               'timestamp' : self._timestamp.isoformat() }

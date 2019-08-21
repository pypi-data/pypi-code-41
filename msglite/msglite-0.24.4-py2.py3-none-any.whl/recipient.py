import logging

from msglite import constants
from msglite.properties import Properties
from msglite.utils import format_party

logger = logging.getLogger(__name__)


class Recipient(object):
    """
    Contains the data of one of the recipients in an msg file.
    """

    def __init__(self, _dir, msg):
        self.__msg = msg  # Allows calls to original msg file
        self.dir = _dir
        self.props = Properties(self._getStream('__properties_version1.0'), constants.TYPE_RECIPIENT)
        self.email = self._getStringStream('__substg1.0_39FE')
        if not self.email:
            self.email = self._getStringStream('__substg1.0_3003')
        self.name = self._getStringStream('__substg1.0_3001')
        # Sender if `type & 0xf == 0`
        # To if `type & 0xf == 1`
        # Cc if `type & 0xf == 2`
        # Bcc if `type & 0xf == 3`
        self.type = self.props.get('0C150003').value
        self.formatted = format_party(self.email, self.name)

    def _getStream(self, filename):
        return self.__msg._getStream([self.dir, filename])

    def _getStringStream(self, filename):
        """
        Gets a string representation of the requested filename.
        Checks for both ASCII and Unicode representations and returns
        a value if possible.  If there are both ASCII and Unicode
        versions, then :param prefer: specifies which will be
        returned.
        """
        return self.__msg._getStringStream([self.dir, filename])

    def Exists(self, filename):
        """
        Checks if stream exists inside the recipient folder.
        """
        return self.__msg.Exists([self.dir, filename])

    def sExists(self, filename):
        """
        Checks if the string stream exists inside the recipient folder.
        """
        return self.__msg.sExists([self.dir, filename])

    def __repr__(self):
        return '<Recipient(%s)>' % self.formatted
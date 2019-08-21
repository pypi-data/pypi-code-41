import logging
import random
import string

from msglite import constants
from msglite.properties import Properties
from msglite.utils import properHex

logger = logging.getLogger(__name__)


class Attachment(object):
    """
    Stores the attachment data of a Message instance.
    Should the attachment be an embeded message, the
    class used to create it will be the same as the
    Message class used to create the attachment.
    """

    def __init__(self, msg, dir_):
        """
        :param msg: the Message instance that the attachment belongs to.
        :param dir_: the directory inside the msg file where the attachment is located.
        """
        self.msg = msg
        self.dir = dir_
        self.props = Properties(self._getStream('__properties_version1.0'),
                                constants.TYPE_ATTACHMENT)
        # Get long filename
        self.longFilename = self._getStringStream('__substg1.0_3707')

        # Get short filename
        self.shortFilename = self._getStringStream('__substg1.0_3704')

        # Get Content-ID
        self.cid = self._getStringStream('__substg1.0_3712')

        # Get attachment data
        self.data = None
        if self.Exists('__substg1.0_37010102'):
            self.type = 'data'
            self.data = self._getStream('__substg1.0_37010102')
        elif self.Exists('__substg1.0_3701000D'):
            if (self.props['37050003'].value & 0x7) != 0x5:
                raise TypeError('Container is not an embedded msg file.')
            self.prefix = msg.prefixList + [dir_, '__substg1.0_3701000D']
            self.type = 'msg'
            self.data = msg.__class__(self.msg.path,
                                      prefix=self.prefix,
                                      filename=self.getDefaultFilename())
        else:
            # TODO Handling for special attachment types (like 0x00000007)
            raise TypeError('Unknown attachment type.')

    def _getStream(self, filename):
        return self.msg._getStream([self.dir, filename])

    def _getStringStream(self, filename):
        """
        Gets a string representation of the requested filename.
        Checks for both ASCII and Unicode representations and returns
        a value if possible.  If there are both ASCII and Unicode
        versions, then :param prefer: specifies which will be
        returned.
        """
        return self.msg._getStringStream([self.dir, filename])

    def Exists(self, filename):
        """
        Checks if stream exists inside the attachment folder.
        """
        return self.msg.Exists([self.dir, filename])

    def sExists(self, filename):
        """
        Checks if the string stream exists inside the attachment folder.
        """
        return self.msg.sExists([self.dir, filename])

    def getDefaultFilename(self):
        # If filename is None at this point, use long filename as first preference  
        if self.longFilename:
            return self.longFilename
        # Otherwise use the short filename
        if self.shortFilename:
            return self.shortFilename
        # Otherwise just make something up!
        return 'Unknown %s.bin' % self.dir

    def __repr__(self):
        return '<Attachment(%s)>' % self.getDefaultFilename()
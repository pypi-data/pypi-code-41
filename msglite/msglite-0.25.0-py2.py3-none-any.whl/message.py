import copy
import logging
import olefile
import email.utils
from email.policy import default
from email.parser import Parser as EmailParser

from msglite import constants
from msglite.attachment import Attachment
from msglite.properties import Properties
from msglite.recipient import Recipient
from msglite.utils import has_len, format_party, guess_encoding

logger = logging.getLogger(__name__)


class Message(olefile.OleFileIO):
    """
    Parser for Microsoft Outlook message files.
    """

    def __init__(self, path, prefix='', filename=None,
                 stringEncoding="utf-16-le"):
        """
        :param path: path to the msg file in the system or is the raw msg file.
        :param prefix: used for extracting embeded msg files
            inside the main one. Do not set manually unless
            you know what you are doing.
        :param filename: optional, the filename to be used by default when
            saving.
        """
        # WARNING DO NOT MANUALLY MODIFY PREFIX. Let the program set it.
        self.encoding = stringEncoding
        self.path = path
        olefile.OleFileIO.__init__(self, path)
        prefixl = []
        tmp_condition = prefix != ''
        if tmp_condition:
            if not isinstance(prefix, str):
                try:
                    prefix = '/'.join(prefix)
                except Exception:
                    raise TypeError('Invalid prefix: ' + str(type(prefix)))
            prefix = prefix.replace('\\', '/')
            g = prefix.split("/")
            if g[-1] == '':
                g.pop()
            prefixl = g
            if prefix[-1] != '/':
                prefix += '/'
        self.prefix = prefix
        self.__prefixList = prefixl
        if tmp_condition:
            addr = prefixl[:-1] + ['__substg1.0_3001']
            filename = self._getStringStream(addr, prefix=False)
        if filename is not None:
            self.filename = filename
        elif has_len(path):
            if len(path) < 1536:
                self.filename = path
            else:
                self.filename = None
        else:
            self.filename = None

        # Parse the main props
        prop_type = constants.TYPE_MESSAGE_EMBED
        if self.prefix == '':
            prop_type = constants.TYPE_MESSAGE
        propdata = self._getStream('__properties_version1.0')
        self.mainProperties = Properties(propdata, prop_type)

        # Determine if the message is unicode-style:
        # PidTagStoreSupportMask
        areStringsUnicode = False
        if self.mainProperties.has_key('340D0003'):
            if (self.mainProperties['340D0003'].value & 0x40000) != 0:
                areStringsUnicode = True

        # Based on that, determine the effecive encoding:
        # PidTagMessageCodepage
        if not areStringsUnicode:
            if self.mainProperties.has_key('3FFD0003'):
                enc = self.mainProperties['3FFD0003'].value
                # Now we just need to translate that value
                # Now, this next line SHOULD work, but it is possible
                # that it might not...
                self.encoding = str(enc)
            else:
                guessed = self.guessEncoding()
                self.encoding = guessed or self.encoding

        self.header = self.parseHeader()
        self.recipients = self.parseRecipients()
        self.attachments = self.parseAttachments()
        self.subject = self._getStringStream('__substg1.0_0037')
        self.date = self.mainProperties.date

    def guessEncoding(self):
        texts = ('1000001E', '1000001F',
                 '1013001E', '1013001F',
                 '0037001E', '0037001F')
        for field in texts:
            raw = self._getStream('__substg1.0_%s' % field)
            encoding = guess_encoding(raw)
            if encoding is not None:
                return encoding

    def listDir(self, streams=True, storages=False):
        """
        Replacement for OleFileIO.listdir that runs at the current
        prefix directory.
        """
        temp = self.listdir(streams, storages)
        if self.prefix == '':
            return temp
        prefix = self.prefix.split('/')
        if prefix[-1] == '':
            prefix.pop()
        out = []
        for x in temp:
            good = True
            if len(x) <= len(prefix):
                good = False
            if good:
                for y in range(len(prefix)):
                    if x[y] != prefix[y]:
                        good = False
            if good:
                out.append(x)
        return out

    def Exists(self, inp):
        """
        Checks if :param inp: exists in the msg file.
        """
        inp = self.fix_path(inp)
        return self.exists(inp)

    def sExists(self, inp):
        """
        Checks if string stream :param inp: exists in the msg file.
        """
        inp = self.fix_path(inp)
        return self.exists(inp + '001F') or self.exists(inp + '001E')

    def fix_path(self, inp, prefix=True):
        """
        Changes paths so that they have the proper
        prefix (should :param prefix: be True) and
        are strings rather than lists or tuples.
        """
        if isinstance(inp, (list, tuple)):
            inp = '/'.join(inp)
        if prefix:
            inp = self.prefix + inp
        return inp

    def _getStream(self, filename, prefix=True):
        filename = self.fix_path(filename, prefix)
        if not self.exists(filename):
            return None
        with self.openstream(filename) as stream:
            return stream.read()

    def _getStringStream(self, filename, prefix=True):
        """
        Gets a string representation of the requested filename.
        This should ALWAYS return a string (Unicode in python 2)
        """
        filename = self.fix_path(filename, prefix)
        for suffix in ('001F', '001E', '0102'):
            data = self._getStream(filename + suffix, prefix=prefix)
            if data is None:
                continue
            # FIXME: should this warn explicitly?
            return data.decode(self.encoding, 'replace')

    def getStringField(self, name):
        return self._getStringStream('__substg1.0_%s' % name)

    @property
    def prefixList(self):
        """
        Returns the prefix list of the Message instance.
        Intended for developer use.
        """
        return copy.deepcopy(self.__prefixList)

    def parseAttachments(self):
        """ Returns a list of all attachments. """
        attachmentDirs = []
        for dir_ in self.listDir():
            if dir_[len(self.__prefixList)].startswith('__attach') and\
                    dir_[len(self.__prefixList)] not in attachmentDirs:
                attachmentDirs.append(dir_[len(self.__prefixList)])

        attachments = []
        for attachmentDir in attachmentDirs:
            attachments.append(Attachment(self, attachmentDir))
        return attachments

    def parseRecipients(self):
        """ Returns a list of all recipients. """
        recipientDirs = []
        for dir_ in self.listDir():
            if dir_[len(self.__prefixList)].startswith('__recip') and\
                    dir_[len(self.__prefixList)] not in recipientDirs:
                recipientDirs.append(dir_[len(self.__prefixList)])

        recipients = []
        for recipientDir in recipientDirs:
            recipients.append(Recipient(recipientDir, self))
        return recipients

    def getRecipientsByType(self, type):
        recipients = []
        for x in self.recipients:
            if x.type & 0x0000000f == type:
                recipients.append(x.formatted)
        return recipients

    def parseHeader(self):
        """ Returns the message header. """
        headerText = self.getStringField('007D')
        headerText = headerText or ''
        parser = EmailParser(policy=default)
        header = parser.parsestr(headerText)
        return header

    def getHeader(self, name):
        try:
            return self.header.get_all(name)
        except (TypeError, IndexError, AttributeError, ValueError) as exc:
            logger.warning("Cannot read header [%s]: %s", name, exc)
            return None

    @property
    def parsedDate(self):
        return email.utils.parsedate(self.date)

    @property
    def sender(self):
        """
        Returns the message sender, if it exists.
        """
        text = self.getStringField('0C1A')
        email = self.getStringField('5D01')
        if email is None:
            email = self.getStringField('0C1F')
        return format_party(email, text)

    @property
    def to(self):
        """ Returns the to field. """
        headerResult = self.getHeader('to')
        if headerResult is not None:
            return headerResult
        return self.getRecipientsByType(1)

    @property
    def cc(self):
        """ Returns the cc field. """
        headerResult = self.getHeader('cc')
        if headerResult is not None:
            return headerResult
        return self.getRecipientsByType(2)

    @property
    def bcc(self):
        """ Returns the bcc field. """
        headerResult = self.getHeader('bcc')
        if headerResult is not None:
            return headerResult
        return self.getRecipientsByType(3)

    @property
    def compressedRtf(self):
        """
        Returns the compressed RTF stream, if it exists.
        """
        return self._getStream('__substg1.0_10090102')

    @property
    def body(self):
        """ Returns the message body. """
        return self.getStringField('1000')

    @property
    def htmlBody(self):
        """
        Returns the html body, if it exists.
        """
        return self.getStringField('1013')

    @property
    def message_id(self):
        message_id = self.getHeader('message-id')
        if message_id is not None:
            return message_id
        return self.getStringField('1035')

    @property
    def references(self):
        message_id = self.getHeader('references')
        if message_id is not None:
            return message_id
        return self.getStringField('1039')

    @property
    def reply_to(self):
        return self._getStringStream('__substg1.0_1042')

    def dump(self):
        """
        Prints out a summary of the message
        """
        print('Message')
        print('Subject:', self.subject)
        print('Date:', self.date)
        print('Body:')
        print(self.body)

    def debug(self):
        for dir_ in self.listDir():
            if dir_[-1].endswith('001E') or dir_[-1].endswith('001F'):
                print('Directory: ' + str(dir_[:-1]))
                print('Contents: {}'.format(self._getStream(dir_)))

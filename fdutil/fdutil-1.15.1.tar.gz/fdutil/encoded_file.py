# encoding: utf-8

from __future__ import unicode_literals
import codecs
import os
from future.builtins import str


class EncodedFile(object):

    def __init__(self,
                 filename,
                 mode='r',
                 encoding='utf-8'):
        try:
            self.ENCODING
        except AttributeError:
            self.ENCODING = encoding
        self.filename = filename
        self.file = None
        self.mode = mode
        self.open()

    def reset(self):
        self.open()

    def write(self,
              string_to_write):
        self.file.write(string_to_write)

    def writeln(self,
                string_to_write):
        self.write('{string}{newline}'.format(string=string_to_write,
                                              newline=os.linesep))

    def writeline(self):
        return self.writeln()

    def readln(self):
        line = self.file.readline()
        if not line:
            return None
        return self.fix_line(self.remove_new_lines(line))

    def readline(self):
        return self.readln()

    def read(self):
        self.reset()
        # Remove additional BOM https://bugs.python.org/issue1701389
        lines = []
        eof = False
        while not eof:
            line = self.file.readline()
            lines.append(self.fix_line(self.remove_new_lines(line)))
            eof = not self.has_new_line(line)
        self.close()
        return '\n'.join(lines)

    @property
    def contents(self):
        return self.read()

    def open(self):
        self.file = codecs.open(filename=self.filename,
                                encoding=self.ENCODING,
                                mode=self.mode)

    def close(self):
        self.file.close()

    @staticmethod
    def has_new_line(line):
        return line.endswith('\n') or line.endswith(os.linesep)

    @staticmethod
    def remove_new_lines(line):
        return line.rstrip(os.linesep).rstrip('\n')

    @staticmethod
    def fix_line(line):
        """
        OVERRIDE in subclass if a fix is required
        :param line:
        :return:
        """
        return line


class UTF8File(EncodedFile):
    ENCODING = 'UTF-8'


class UTF16File(EncodedFile):
    ENCODING = 'utf-16'

    @staticmethod
    def fix_line(line):
        return line.lstrip('\ufeff')

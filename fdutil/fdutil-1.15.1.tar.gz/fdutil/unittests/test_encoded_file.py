# encoding: utf-8

from __future__ import unicode_literals
import unittest
import os
from fdutil.encoded_file import EncodedFile, UTF8File, UTF16File


class TestEncodedFile(unittest.TestCase):

    TEST_DATA = """â
âêîôûŷŵÂÊÎÔÛŴŶ
line2
[§2]
"""

    def runner(self,
               FileReaderWriter,
               filename,
               test_data):

        lines = test_data.splitlines()

        x = FileReaderWriter(filename, 'w')
        x.writeln(lines.pop(0))
        x.close()

        x = FileReaderWriter(filename, 'a')
        while lines:
            line = lines.pop(0)
            x.writeln(line)
        x.close()

        lines = test_data.splitlines()

        x = FileReaderWriter(filename, 'r')
        while lines:
            line = x.readline()
            expected = lines.pop(0)
            assert line == expected, (line, expected)
        x.close()

        assert x.contents == test_data, ('whole file:\n'
                                         '"""{contents}"""\n'
                                         'test data:\n'
                                         '"""{test_data}"""'
                                         .format(contents=x.contents,
                                                 test_data=test_data))

        os.remove(filename)

    def test_default(self):
        self.runner(EncodedFile,
                    'EncodedFileTest.txt',
                    self.TEST_DATA)

    def test_utf8(self):
        self.runner(UTF8File,
                    'UTF8File.txt',
                    self.TEST_DATA)

    def test_utf16(self):
        self.runner(UTF16File,
                    'UTF16File.txt',
                    self.TEST_DATA)


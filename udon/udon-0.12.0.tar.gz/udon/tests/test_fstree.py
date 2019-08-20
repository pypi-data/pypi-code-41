import os
import tempfile
import unittest
import hashlib

import udon.fstree


class TestFSTree(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.count = 0

    def tearDown(self):
        self.tmpdir.cleanup()

    def content(self, path = None):
        if path is None:
            path = os.path.join(self.tmpdir.name, "file-%d" % self.count)
            self.count += 1
        return udon.content.ContentFile(path)

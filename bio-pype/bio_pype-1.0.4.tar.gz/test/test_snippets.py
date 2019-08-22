import unittest
import sys
import os
import argparse
from pype.modules import snippets
from pype.misc import generate_uid

try:
    from cStringIO import StringIO
except:
    try:
        from StringIO import StringIO
    except:
        from io import StringIO


class TestSnippets(unittest.TestCase):

    def setUp(self):
        self.held, sys.stdout = sys.stdout, StringIO()
        self.parser = argparse.ArgumentParser(prog='pype', description='Test')
        self.subparsers = self.parser.add_subparsers(dest='modules')

    def test_snippets(self):
        a = generate_uid()
        b = generate_uid()
        snippets.snippets(None, self.subparsers, None, [
                          '--log', 'test/data/tmp', 'test', '--test', a], 'test')
        self.assertEqual(sys.stdout.getvalue(), 'Hello %s\n' % a)
        snippets.snippets(None, self.subparsers, 'test', [
                          '--log', 'test/data/tmp', 'test', '--test', b, '-o', a], 'test')
        self.assertEqual(sys.stdout.getvalue(),
                         'Hello %s\n%s %s\n' % (a, a, b))

    def tearDown(self):
        sys.stdout = self.held

if __name__ == '__main__':
    unittest.main()

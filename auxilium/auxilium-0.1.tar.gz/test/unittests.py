# -*- coding: utf-8 -*-

# auxilium
# --------
# A Python project for an automated test and deploy toolkit - 100%
# reusable.
# 
# Author:   sonntagsgesicht
# Version:  0.1, copyright Thursday, 29 August 2019
# Website:  https://github.com/sonntagsgesicht/auxilium
# License:  Apache License 2.0 (see LICENSE file)


import sys
import os
import unittest
import logging
import datetime
import shutil

pkg = __import__(os.getcwd().split(os.sep)[-1])

logging.basicConfig()


class CreateRepoUnitTests(unittest.TestCase):
    def setUp(self):
        self.wdir = 'test_create_repo'
        self.name = 'unicorn'
        self.doc = 'Always be a unicorn.'
        self.author = 'dreamer'
        self.email = '<name>@home'

    def test_create_repo(self):
        if os.path.exists(self.wdir):
            shutil.rmtree(self.wdir)
        os.mkdir(self.wdir)
        os.chdir(self.wdir)

        inputs = self.name, self.doc, self.author, self.email
        with open('%s_details' % self.name, "w") as f:
            f.write(os.linesep.join(inputs))
        if os.system("auxilium create < %s_details" %self.name):
            raise Exception()

        os.chdir(self.name)
        self.assertEqual(os.getcwd().split(os.sep)[-1], self.name)

        if sys.version.startswith('3.7'):
            cmd = 'auxilium full'
        else:
            cmd = 'auxilium simple'

        if os.system(cmd):
            raise Exception()


if __name__ == "__main__":
    start_time = datetime.datetime.now()

    print('')
    print('======================================================================')
    print('')
    print(('run %s' % __file__))
    print(('in %s' % os.getcwd()))
    print(('started  at %s' % str(start_time)))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    unittest.main(verbosity=2)

    print('')
    print('======================================================================')
    print('')
    print(('ran %s' % __file__))
    print(('in %s' % os.getcwd()))
    print(('started  at %s' % str(start_time)))
    print(('finished at %s' % str(datetime.datetime.now())))
    print('')
    print('----------------------------------------------------------------------')
    print('')

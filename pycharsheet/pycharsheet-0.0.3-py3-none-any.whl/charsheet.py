# Copyright © 2019 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

from .error import ExitError

class Charsheet:
    def bye(self):
        print('bye!')
        raise ExitError()

    exit = bye

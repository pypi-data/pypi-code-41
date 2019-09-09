#!/usr/bin/env python3

# Copyright (c) 2019 Kai Hoewelmeyer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
from check_copyright.filter_files import matching_files

CHECK_EXTENSIONS = ["*.cpp", "*.h", "*.py", "*.sh"]
LICENSE_FILE = os.path.realpath(os.path.join(".", "LICENSE"))
WHITESPACE_TRANSLATION= {
        ord('#'): None,
        ord('/'): None,
        ord('*'): None,
        ord(' '): None
}

if not os.path.exists(LICENSE_FILE):
    print("Cannot find LICENSE", file=sys.stderr)
    sys.exit(1)

LICENSE = " ".join(open(LICENSE_FILE).read().splitlines(False))
STRIPPED_LICENSE = LICENSE.translate(WHITESPACE_TRANSLATION)

def check_copyright(filename):
    with open(filename) as f:
        head_file = " ".join(f.read(len(LICENSE) + 100).splitlines(False))
        stripped_file = head_file.translate(WHITESPACE_TRANSLATION)
        if not STRIPPED_LICENSE in stripped_file:
            print("%s is missing copyright header" % filename, file=sys.stderr)
            return False
        return True


def check_all_files():
    if not all([check_copyright(x) for x in matching_files(".", CHECK_EXTENSIONS)]):
        print("Not all files have correct copyrights", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    check_all_files()


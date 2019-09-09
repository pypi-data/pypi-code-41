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
from fnmatch import fnmatch
dir_path = os.path.dirname(os.path.realpath(__file__))


def is_matching_file(file, glob_patterns):
    return any([fnmatch(file, pattern) for pattern in glob_patterns])


def is_hidden_dir(dirname):
    return fnmatch(dirname, "**/.*")


def is_ignored_dir(dirname):
    benchmark_path = os.path.realpath(os.path.join(dir_path, "benchmarks"))
    abs_dirname = os.path.realpath(dirname)
    return os.path.commonpath([benchmark_path, abs_dirname]) == benchmark_path


def matching_files(root, glob_patterns):
    for root, dirs, files in os.walk(root):
        if is_hidden_dir(root): continue
        if is_ignored_dir(root): continue
        for file in files:
            if is_matching_file(file, glob_patterns):
                yield os.path.join(root, file)


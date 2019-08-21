'''
MIT License

Copyright (c) 2019 Hyeonki Hong

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

from setuptools import setup, find_packages, Extension
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

print("\n\n\n\n\n\nhahahahahaha\n\n\n\n\n")

classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: POSIX :: Linux",
    "Intended Audience :: Developers",
    "Topic :: Software Development",
    "Topic :: System :: Hardware",
]

ext_modules = [
    Extension(
        "Odroid._GPIO",
        [
            path.join(here, "lib/wrap/wiringPi_wrap.i")
        ],
        libraries = ["wiringPi", "wiringPiDev", "m", "pthread", "rt", "crypt"],
    ),
]

setup(
    name                            = "Odroid.GPIO",
    version                         = "0.0.1b",
    description                     = "A module to control Odroid GPIO channels",
    long_description                = long_description,
    long_description_content_type   = "text/markdown",
    url                             = "https://github.com/hhk7734/odroid_gpio",
    author                          = "Hyeonki Hong",
    author_email                    = "hhk7734@gmail.com",    
    classifiers                     = classifiers,
    keywords                        = ["Odroid", "GPIO"],
    package_dir                     = {"": "lib/python/"},
    packages                        = find_packages(),
    license                         = "MIT",
    ext_modules                     = ext_modules,
    project_urls                    = {
                                        'Source': 'https://github.com/hhk7734/odroid_gpio',
                                    },
)

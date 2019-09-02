# -*- coding: utf-8 -*-

import setuptools


NAME = "idingtalk"
VERSION = "0.0.5"
LICENSE = "MIT"
KEYWORDS = "idingtalk, Dingding, DingTalk, incoming"
AUTHOR = "teachmyself"
AUTHOR_EMAIL = "teachmyself@126.com"
DESCRIPTION = "Dingtalk tools."
LONG_DESCRIPTION = ""
LONG_DESCRIPTION_TYPE = "text/markdown"
URL = "https://pypi.org/project/idingtalk/"
INSTALL_REQUIRES = ["requests"]
STATUS = "5 - Production/Stable"


with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()


setuptools.setup(
    name=NAME,
    version=VERSION,
    license=LICENSE,
    keywords=KEYWORDS,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: %s' % (STATUS),
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: %s License' % (LICENSE),
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation
# All rights reserved.
#-------------------------------------------------------------------------

import os

NOTICE = os.path.join(os.path.abspath(__file__), '..', 'NOTICE.rst')
with open(NOTICE, 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup_cfg = dict(
    name='onedrivesdk',
    version='2.0',
    description='Deprecated OneDrive SDK. Install `onedrivesdk<2` for legacy versions.',
    long_description=LONG_DESCRIPTION,
    author='Microsoft Corporation',
    author_email='python@microsoft.com',
    url='https://docs.microsoft.com/graph/onedrive-concept-overview',
    packages=['onedrivesdk'],
)

from distutils.core import setup
setup(**setup_cfg)

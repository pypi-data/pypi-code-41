import os
import pkg_resources


__copyright__ = 'Copyright (C) 2019, Nokia'


TEMPLATE_DIR = os.path.join(
    pkg_resources.resource_filename('crl.doc', os.path.join('resource', 'templates')))

TOC_TEMPLATE = os.path.join(TEMPLATE_DIR, 'toc.rst')

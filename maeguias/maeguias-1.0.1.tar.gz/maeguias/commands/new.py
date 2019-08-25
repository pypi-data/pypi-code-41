# coding: utf-8
from __future__ import unicode_literals

import io
import logging
import os

config_text = 'site_name: MAE\n'
index_text = """# Bienvenido a MaeGuias
"""

log = logging.getLogger(__name__)


def new(output_dir):

    docs_dir = os.path.join(output_dir, 'docs')
    config_path = os.path.join(output_dir, 'maeguias.yml')
    index_path = os.path.join(docs_dir, 'index.md')

    if os.path.exists(config_path):
        log.info('Project already exists.')
        return

    if not os.path.exists(output_dir):
        log.info('Creating project directory: %s', output_dir)
        os.mkdir(output_dir)

    log.info('Writing config file: %s', config_path)
    io.open(config_path, 'w', encoding='utf-8').write(config_text)

    if os.path.exists(index_path):
        return

    log.info('Writing initial docs: %s', index_path)
    if not os.path.exists(docs_dir):
        os.mkdir(docs_dir)
    io.open(index_path, 'w', encoding='utf-8').write(index_text)

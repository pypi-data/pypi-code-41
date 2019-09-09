from pelican import signals

import multiprocessing
import htmlmin
import os
import re

import logging
logger = logging.getLogger(__name__)


def run(pelican):

    # should we run or not
    if pelican.settings.get(
            'HTMLMIN_DEBUG',
            logger.getEffectiveLevel() == logging.DEBUG
    ):
        # HTMLMIN_DEBUG is True or Pelican is in DEBUG mode
        # Don't minify the output to help with debugging
        return

    options = pelican.settings.get(
        'HTMLMIN_OPTIONS',
        {
            'remove_commends': True,
            'remove_all_empty_space': True,
            'remove_optional_attribute_quotes': False
        }
    )
    htmlfile = re.compile(
        pelican.settings.get('HTMLMIN_MATCH', r'.html?$')
    )
    pool = multiprocessing.Pool()

    # find all matching files and give to workers to minify
    for base, dirs, files in os.walk(pelican.settings['OUTPUT_PATH']):
        for f in filter(htmlfile.search, files):
            filepath = os.path.join(base, f)
            pool.apply_async(worker, (filepath, options))

    # wait for the workers to finish
    pool.close()
    pool.join()


def worker(filepath, options):
    """use htmlmin to minify the given file"""
    rawhtml = open(filepath, encoding='utf-8').read()
    with open(filepath, 'w', encoding='utf-8') as f:
        logger.debug('Minifying: %s', filepath)
        try:
            compressed = htmlmin.minify(rawhtml, **options)
            f.write(compressed)
        except Exception as e:
            logger.critical('Minification failed: %s', e)


def register():
    """minify HTML at the end of the pelican build"""
    signals.finalized.connect(run)

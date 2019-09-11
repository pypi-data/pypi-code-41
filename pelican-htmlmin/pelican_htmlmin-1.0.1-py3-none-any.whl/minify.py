from pelican import signals

import multiprocessing
import htmlmin
import os
import re

import logging
logger = logging.getLogger(__name__)


def run(pelican):

    # should we be minifying HTML files
    if pelican.settings.get(
            'HTMLMIN_ENABLED',
            not logger.getEffectiveLevel() <= logging.DEBUG
    ) is False:
        logger.debug("'pelican-htmlmin' disabled")
        return

    options = pelican.settings.get(
        'HTMLMIN_OPTIONS',
        {
            'remove_comments': True,
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

    # copy file into memory while we minify it
    with open(filepath, encoding='utf-8') as f:
        rawhtml = f.read()

    # minify 'rawhtml' and save the minified
    # version back to the same location
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

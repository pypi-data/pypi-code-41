import argparse
import io
import logging
import re
from urlparse import urljoin
from zipfile import ZipFile

from lxml import etree, html
import requests


__version__ = '1.0.1'


LATEX_PAGE_URL = 'https://journals.plos.org/plosone/s/latex'
TEMPLATE_LINK_XPATH = etree.XPath('//a[text() = "PLOS template"]/@href', smart_strings=False)
TEMPLATE_FILENAME = 'plos_latex_template.tex'
TEMPLATE_VERSION_RE = re.compile(r'Version ([0-9.]+)')


def find_template_url():
    # ``html.parse`` can't work with HTTPS resources, so use ``requests.get``
    # to get the URLs content and then parse it with ``html.fromstring``.
    r = requests.get(LATEX_PAGE_URL)
    r.raise_for_status()

    document = html.fromstring(r.text)
    template_url = TEMPLATE_LINK_XPATH(document)[0]
    template_url = urljoin(LATEX_PAGE_URL, template_url) # Convert it to an absolute URL

    return template_url

def open_template_file(template_url):
    r = requests.get(template_url)
    r.raise_for_status()

    # ``io.BytesIO`` wrapper is required as ``zipfile.ZipFile`` needs a seekable
    # file-like object for its input, whereas ``r.raw.seek`` is an unsupported
    # operation.
    zip_fileobj = ZipFile(io.BytesIO(r.content))
    return zip_fileobj.read(TEMPLATE_FILENAME)

def parse_template_file(template_file):
    match = TEMPLATE_VERSION_RE.search(template_file)
    return match.group(1) if match else 'UNKNOWN'

def get_template_version():
    template_url = find_template_url()
    template_file = open_template_file(template_url)
    template_version = parse_template_file(template_file)

    logging.info("Parsed the PLOS LaTeX template, found version %s", template_version)
    return template_version

def compare_versions(reference, parsed_version):
    if reference != parsed_version:
        logging.warn("A newer version of the PLOS LaTeX template has been found (%s > %s)", parsed_version, reference)
    else:
        logging.info("PLOS LaTeX template is at the latest version")

def main():
    # Setup command line option parser
    parser = argparse.ArgumentParser(
        description='Automated tracking of PLOS LaTeX template versions',
    )
    parser.add_argument(
        '-c',
        '--check',
        metavar='VERSION',
        help="Check if there's a newer version of the PLOS LaTeX template than the one provided"
    )
    parser.add_argument(
        '-q',
        '--quiet',
        action='store_const',
        const=logging.WARN,
        dest='verbosity',
        help='Be quiet, show only warnings and errors',
    )
    parser.add_argument(
        '-v',
        '--verbose',
        action='store_const',
        const=logging.DEBUG,
        dest='verbosity',
        help='Be very verbose, show debug information',
    )
    parser.add_argument(
        '--version',
        action='version',
        version="%(prog)s " + __version__,
    )
    args = parser.parse_args()

    # Configure logging
    log_level = args.verbosity or logging.INFO
    logging.basicConfig(level=log_level, format="[%(levelname)s] %(message)s")

    template_version = get_template_version()
    if args.check:
        compare_versions(args.check, template_version)

if __name__ == '__main__':
    main()

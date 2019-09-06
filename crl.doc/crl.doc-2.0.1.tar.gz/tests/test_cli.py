import logging
from six.moves import range
from crl.doc.docargparser import (
    DESCRIPTION,
    DOCSPEC_HELP,
    LIBPATH_HELP,
    RESOURCE_HELP)
import crl.doc


__copyright__ = 'Copyright (C) 2019, Nokia'

LOGGER = logging.getLogger(__name__)
CLI = 'crl_doc_generate_rst'
EXPECTED_HELPS = [DESCRIPTION, DOCSPEC_HELP, LIBPATH_HELP, RESOURCE_HELP]


def test_cli(cliverifier):
    cliverifier.verify()


def test_cli_help(script_runner):
    ret = script_runner.run(CLI, '-h')
    for h in EXPECTED_HELPS:
        assert _contains(h.split(), ret.stdout.split())


def _contains(a, b):
    la = len(a)
    for i in range(len(b) - la + 1):
        if a == b[i:i + la]:
            return True
    return False


def test_cli_version(script_runner):
    ret = script_runner.run(CLI, '--version')
    assert '{cli} {version}'.format(
        cli=CLI,
        version=crl.doc.__version__) == ret.stdout.strip()

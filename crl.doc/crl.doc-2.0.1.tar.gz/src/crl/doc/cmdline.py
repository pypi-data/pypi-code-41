import logging
from .docargparser import DocArgParser
from .crldocbuilder import CRLDocBuilder
from .crldocutils import error_handling


__copyright__ = 'Copyright (C) 2019, Nokia'


def cmdline():
    """
    Command line interface for generating documentation from
    Robot BuiltIn libraries,
    Common Robot Libraries and UTE common API.

    """
    with error_handling('CRL documentation generation failed', sys_exit=1):
        _setup_crldoc_loggers()
        parser = DocArgParser()
        _create_doc(parser.args)


def _setup_crldoc_loggers():
    logger = logging.getLogger('crl.doc')
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())


def _create_doc(args):
    docbuilder = CRLDocBuilder(args)
    docbuilder.create_doc()

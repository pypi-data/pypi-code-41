import logging
import os
import subprocess
import prophesy.config
from prophesy.smt.smtlib import SmtlibSolver, parse_smt_command, parse_smt_expr
from prophesy.smt.smt import Answer
from prophesy import util

logger = logging.getLogger(__name__)

class IcpCliSolver(SmtlibSolver):
    """
    TODO: support the soft timeout kill.
    """


    def __init__(self, location=None, memout=4000, timeout=None):
        from prophesy.config import configuration
        super().__init__(location if location is not None else configuration.get_smtrat_icp(),
                         memout if memout is not None else configuration.get_smt_memout(),
                         timeout if timeout is not None else configuration.get_smt_timeout(), False)
        util.ensure_dir_exists(configuration.get_intermediate_dir())

    def _call_process(self, args):
        self.process = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, universal_newlines=True)


    def name(self):
        return "SMT-rat(icp) cli tool"

    def _additional_args(self):
        return ['-']

    def _build_model(self, output):
        #print(output)
        logger.warning("Generation of models is not supported")
        return None







"""
Initial point generation for the QCQP solvers for the OPF problem.
"""

import logging

import numpy as np

from hynet.types_ import hynet_float_, SolverType, SolverStatus
from hynet.system.initial_point import InitialPointGenerator
from hynet.opf.model import OPFModel
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.solver import SolverInterface
from hynet.utilities.base import Timer
from hynet.reduction.copper_plate import reduce_to_copper_plate

_log = logging.getLogger(__name__)


class CopperPlateInitialPointGenerator(InitialPointGenerator):
    """
    Copper plate based initial point generator for the QCQP OPF solvers.

    This generator returns an initial point for the solution of the OPF QCQP
    that comprises the optimal dispatch of the copper plate reduction of the
    model. The copper plate solution is typically fast to compute and can
    reduce the number of iterations required to solve the nonconvex QCQP, i.e.,
    it can improve the overall performance when solving the nonconvex problem.
    """
    def __init__(self, solver):
        """
        Initialize the generator with a particular solver.

        Parameters
        ----------
        solver : SolverInterface
            SOCR solver for the initial point computation.
        """
        if not isinstance(solver, SolverInterface) or \
                solver.type != SolverType.SOCR:
            raise ValueError("Expecting an SOCR solver interface.")
        self._solver = solver

    @property
    def solver(self):
        """Return the solver for the initial point computation."""
        return self._solver

    def __call__(self, model, qcqp):
        timer = Timer()
        initial_point = None
        try:
            cp = OPFModel(reduce_to_copper_plate(model.scenario),
                          verify_scenario=False)
            cp_result = self._solver.solve(cp.get_problem())
            if cp_result.solver_status != SolverStatus.SOLVED:
                raise RuntimeError("OPF failed with status '"
                                   + str(cp_result.solver_status) + "'.")
            initial_point = QCQPPoint(v=0.35 * qcqp.lb.v + 0.65 * qcqp.ub.v,
                                      f=np.zeros(qcqp.dim_f, dtype=hynet_float_),
                                      s=cp_result.optimizer.s * qcqp.normalization.s,
                                      z=np.zeros(qcqp.dim_z, dtype=hynet_float_))
        except RuntimeError as exception:
            _log.warning("Copper plate initialization failed: " + str(exception))
        _log.debug("Copper plate initial point calculation ({:.3f} sec.)"
                   .format(timer.total()))
        return initial_point

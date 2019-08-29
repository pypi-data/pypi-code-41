"""
Initial point generation for the QCQP solvers for the OPF problem.
"""

import logging
import abc

import numpy as np

from hynet.types_ import SolverType, SolverStatus
from hynet.opf.model import SystemModel
from hynet.qcqp.problem import QCQPPoint
from hynet.qcqp.solver import SolverInterface
from hynet.utilities.base import Timer

_log = logging.getLogger(__name__)


class InitialPointGenerator(abc.ABC):
    """
    Abstract base class for initial point generators for the QCQP OPF solvers.

    Derived classes implement the generation of an initial point for solvers
    that solve the nonconvex QCQP representation of the OPF problem. With the
    provision of an appropriate initial point, the convergence performance
    and "quality" of the identified local optimum may be improved.
    """
    @abc.abstractmethod
    def __call__(self, model, qcqp):
        """
        Return an initial point for the given OPF QCQP.

        Parameters
        ----------
        model : SystemModel
            Steady-state system model, for which the OPF shall be calculated.
        qcqp : QCQP
            QCQP for the OPF of the given model, for which the initial point
            shall be determined.

        Returns
        -------
        initial_point : QCQPPoint or None
            Initial point for the given OPF QCQP. In case that the initial
            point generation failed, ``None`` is returned.
        """


class RelaxationInitialPointGenerator(InitialPointGenerator):
    """
    Relaxation-based initial point generator for QCQP solvers.

    This generator returns an initial point for the solution of the QCQP
    that corresponds to a relaxation of the QCQP. Especially the second-order
    cone relaxation (SOCR solvers) is typically fast to compute and may be
    suitable.
    """
    def __init__(self, solver, rec_mse_thres=1e-8):
        """
        Initialize the generator with a particular solver.

        Parameters
        ----------
        solver : SolverInterface
            Relaxation-based solver for the initial point computation.
        rec_mse_thres : float
            If the mean squared error of the reconstructed (bus voltage) vector
            ``v`` exceeds this limit (default ``1e-8``), only the modulus of
            its elements is considered in the initial point.
        """
        if not isinstance(solver, SolverInterface) or \
                solver.type == SolverType.QCQP:
            raise ValueError("Expecting a relaxation-based solver interface.")
        self._solver = solver
        self.rec_mse_thres = rec_mse_thres

    @property
    def solver(self):
        """Return the solver for the initial point computation."""
        return self._solver

    def __call__(self, model, qcqp):
        timer = Timer()
        initial_point = None
        try:
            result = self._solver.solve(qcqp)
            if result.solver_status != SolverStatus.SOLVED:
                raise RuntimeError("Failed to solve the problem (status '{:s}')."
                                   .format(result.solver_status.name))
            initial_point = result.optimizer.scale(qcqp.normalization)
            if result.reconstruction_mse > self.rec_mse_thres:
                initial_point.v = np.abs(initial_point.v)
        except RuntimeError as exception:
            _log.warning("{0}-based initialization failed: {1}"
                         .format(self._solver.type.value, str(exception)))
        _log.debug("{0}-based initial point calculation ({1:.3f} sec.)"
                   .format(self._solver.type.value, timer.total()))
        return initial_point

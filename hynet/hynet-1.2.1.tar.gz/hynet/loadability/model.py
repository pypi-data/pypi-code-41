"""
Model to evaluate the maximum loadability of a system with *hynet*.
"""

import logging

import numpy as np
from scipy.sparse import coo_matrix

from hynet.types_ import hynet_float_, hynet_sparse_, ConstraintType
from hynet.utilities.base import (create_sparse_matrix,
                                  create_sparse_zero_matrix,
                                  Timer)
from hynet.scenario.representation import Scenario
from hynet.system.model import SystemModel
from hynet.qcqp.problem import ObjectiveFunction, Constraint
from hynet.loadability.result import LoadabilityResult

_log = logging.getLogger(__name__)


class LoadabilityModel(SystemModel):
    """
    Maximum loadability model for a steady-state scenario of a grid.

    Based on the specification of a scenario via a ``Scenario`` object, this
    class provides the methods to generate a quadratically constrained
    quadratic program (QCQP) that captures the maximum loadability problem.
    The maximum loadability problem is considered as in equations (1) - (3)
    in [1]_ based on the feasibility set of the OPF problem in *hynet*, i.e.,
    *hynet*'s the power balance equations are extended with a scaled load
    increment and the scaling of the increment is maximized. The nodal load
    increment is defined by the column ``'load_increment'`` in the ``bus`` data
    frame of the scenario. If this column is not present, the load increment is
    set to the nodal load (i.e., the ``'load'`` column of the ``bus`` data
    frame), which maintains a constant power factor at the loads.

    See Also
    --------
    hynet.scenario.representation.Scenario:
        Specification of a steady-state grid scenario.
    hynet.loadability.calc.calc_loadability:
        Calculate the maximum loadability.

    References
    ----------
    .. [1] G. D. Irisarri, X. Wang, J. Tong and S. Mokhtari, "Maximum
           loadability of power systems using interior point nonlinear
           optimization method," IEEE Trans. Power Syst., vol. 12, no. 1,
           pp. 162-172, Feb. 1997.
    """

    def __init__(self, scenario, verify_scenario=True):
        """
        Initialize the loadability model with the scenario data.

        Parameters
        ----------
        scenario : Scenario
            Steady-state scenario data for the model.
        verify_scenario : bool, optional
            If ``True`` (default), an integrity and validity check is performed
            on the provided scenario data (see ``Scenario.verify``). In case it
            is ensured beforehand that the provided data is consistent and
            valid, this check may be skipped to improve performance.
        """
        if 'load_increment' not in scenario.bus.columns:
            scenario.bus['load_increment'] = scenario.bus['load'].copy()

        if np.any(scenario.bus['load_increment'].to_numpy().real < 0):
            _log.warning("Some active power load increments are negative.")

        super().__init__(scenario, verify_scenario=verify_scenario)

    @property
    def dim_z(self):
        """
        Return the dimension of the state variable ``z``.

        The loadability problem only requires a single auxiliary variable,
        which is the nonnegative scaling factor for the load increment.
        """
        return 1

    def get_z_bounds(self):
        """
        Return the auxiliary variable bounds ``z_lb <= z <= z_ub``.

        The lower is set to zero and the upper bound is omitted.
        """
        z_lb = np.zeros(self.dim_z, dtype=hynet_float_)
        z_ub = np.full(self.dim_z, fill_value=np.nan, dtype=hynet_float_)
        return z_lb, z_ub

    def get_balance_constraints(self):
        """
        Return the active and reactive power balance constraints.

        For the loadability problem, the power balance equations are augmented
        by a scaled load increment term, where the scaling is maximized by the
        objective.
        """
        timer = Timer()
        N_V = self._scr.num_buses
        index = self._scr.bus.index

        crt_p = np.ndarray(N_V, dtype=Constraint)
        crt_q = np.ndarray(N_V, dtype=Constraint)

        C_p, C_q, c_p, c_q, a_p, a_q, load, scaling = \
            self._get_balance_coefficients()

        # Extract the load increment and scale it properly
        load_increment = \
            self._scr.bus['load_increment'].to_numpy() / self._scr.base_mva
        load_increment *= scaling

        # CAVEAT: For better performance, the type conversion in the loop below
        # is made via .tocoo(). Update the code if the format has changed.
        assert hynet_sparse_ is coo_matrix

        for n in range(N_V):
            # Active power balance
            crt_p[n] = Constraint(name='bal_p',
                                  table='bus',
                                  id=index[n],
                                  C=C_p[n],
                                  c=c_p[:, n].tocoo(),
                                  a=a_p[:, n].tocoo(),
                                  r=create_sparse_matrix([0], [0],
                                                         [load_increment[n].real],
                                                         self.dim_z, 1,
                                                         dtype=hynet_float_),
                                  b=-load[n].real,
                                  scaling=scaling / self._scr.base_mva)

            # Reactive power balance
            crt_q[n] = Constraint(name='bal_q',
                                  table='bus',
                                  id=index[n],
                                  C=C_q[n],
                                  c=c_q[:, n].tocoo(),
                                  a=a_q[:, n].tocoo(),
                                  r=create_sparse_matrix([0], [0],
                                                         [load_increment[n].imag],
                                                         self.dim_z, 1,
                                                         dtype=hynet_float_),
                                  b=-load[n].imag,
                                  scaling=scaling / self._scr.base_mva)

        _log.debug("Power balance constraints ({:.3f} sec.)"
                   .format(timer.total()))
        return ConstraintType.EQUALITY, [crt_p, crt_q]

    def _get_constraint_generators(self):
        """
        Return a list with all constraint generators for the loadability problem.
        """
        return [self.get_balance_constraints,
                self.get_source_ampacity_constraints,
                self.get_destination_ampacity_constraints,
                self.get_real_part_constraints,
                self.get_angle_constraints,
                self.get_voltage_constraints,
                self.get_drop_constraints,
                self.get_converter_polyhedron_constraints,
                self.get_injector_polyhedron_constraints]

    def _get_objective(self):
        """
        Return the objective function for the loadability problem.
        """
        return ObjectiveFunction(C=create_sparse_zero_matrix(self.dim_v,
                                                             self.dim_v),
                                 c=create_sparse_zero_matrix(self.dim_f, 1),
                                 a=create_sparse_zero_matrix(self.dim_s, 1),
                                 r=create_sparse_matrix([0], [0], [-1],
                                                        self.dim_z, 1,
                                                        dtype=hynet_float_),
                                 scaling=1.0)

    def create_result(self, qcqp_result, total_time=np.nan, qcqp_result_pre=None):
        """
        Create and return a loadability result object.

        Parameters
        ----------
        qcqp_result : hynet.qcqp.result.QCQPResult
            Solution of the loadability QCQP.
        total_time : .hynet_float_, optional
            Total time for solving the loadability problem.
        qcqp_result_pre : QCQPResult, optional
            Pre-solution of the loadability QCQP for converter mode detection.

        Returns
        -------
        result : hynet.loadability.result.LoadabilityResult
        """
        return LoadabilityResult(self,
                                 qcqp_result,
                                 total_time=total_time,
                                 qcqp_result_pre=qcqp_result_pre)

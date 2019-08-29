"""
Optimal power flow model of *hynet*.
"""

import logging

import numpy as np

from hynet.types_ import hynet_float_, hynet_sparse_
from hynet.utilities.base import create_sparse_zero_matrix
from hynet.system.model import SystemModel
from hynet.qcqp.problem import ObjectiveFunction
from hynet.opf.result import OPFResult

_log = logging.getLogger(__name__)


class OPFModel(SystemModel):
    """
    Optimal power flow model for a steady-state scenario of a grid.

    Based on the specification of a scenario via a ``Scenario`` object, this
    class provides the methods to generate a quadratically constrained
    quadratic program (QCQP) that captures the optimal power flow problem.

    See Also
    --------
    hynet.scenario.representation.Scenario:
        Specification of a steady-state grid scenario.
    hynet.opf.calc.calc_opf:
        Calculate an optimal power flow.
    """

    def __init__(self, scenario, verify_scenario=True):
        """
        Initialize the OPF model with the scenario data.

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
        super().__init__(scenario, verify_scenario=verify_scenario)
        self._cost_scaling = select_cost_scaling(scenario)

    def _get_constraint_generators(self):
        """
        Return a list with all constraint generation functions for the OPF.
        """
        return [self.get_balance_constraints,
                self.get_source_ampacity_constraints,
                self.get_destination_ampacity_constraints,
                self.get_real_part_constraints,
                self.get_angle_constraints,
                self.get_voltage_constraints,
                self.get_drop_constraints,
                self.get_converter_polyhedron_constraints,
                self.get_injector_polyhedron_constraints,
                self.get_cost_epigraph_constraints]

    def _get_objective(self):
        """
        Return the objective function for the OPF problem.
        """
        N_I = self._scr.num_injectors

        if self._scr.loss_price != 0:
            (obj_C, obj_c) = self.get_dyn_loss_function()
            obj_C *= self._scr.loss_price * self._cost_scaling
            obj_c *= self._scr.loss_price * self._cost_scaling
        else:
            obj_C = create_sparse_zero_matrix(self.dim_v, self.dim_v)
            obj_c = create_sparse_zero_matrix(self.dim_f, 1)

        obj_r = np.zeros((self.dim_z, 1), dtype=hynet_float_)
        obj_r[:2*N_I, 0] = 1  # Cost function epigraph ordinate variables

        return ObjectiveFunction(C=obj_C,
                                 c=obj_c,
                                 a=create_sparse_zero_matrix(self.dim_s, 1),
                                 r=hynet_sparse_(obj_r),
                                 scaling=self._cost_scaling)

    def create_result(self, qcqp_result, total_time=np.nan, qcqp_result_pre=None):
        """
        Create and return an OPF result object.

        Parameters
        ----------
        qcqp_result : hynet.qcqp.result.QCQPResult
            Solution of the OPF QCQP.
        total_time : .hynet_float_, optional
            Total time for solving the OPF, cf. ``hynet.opf.calc.calc_opf``.
        qcqp_result_pre : QCQPResult, optional
            Pre-solution of the OPF QCQP for converter mode detection.

        Returns
        -------
        result : hynet.opf.result.OPFResult
        """
        return OPFResult(self,
                         qcqp_result,
                         total_time=total_time,
                         qcqp_result_pre=qcqp_result_pre)


def select_cost_scaling(scenario):
    """
    Return a suitable scaling factor for the objective of the OPF problem.
    """
    cost_p = scenario.injector['cost_p'].to_numpy()
    cost_q = scenario.injector['cost_q'].to_numpy()
    cap = scenario.injector['cap'].to_numpy()
    load = scenario.bus['load'].to_numpy()

    max_cost = 0
    for (f_p, f_q, cr) in zip(cost_p, cost_q, cap):
        if f_p is not None:
            max_cost = np.max([max_cost,
                               np.max(np.abs(
                                   f_p.evaluate([cr.p_min, cr.p_max])))])
        if f_q is not None:
            max_cost = np.max([max_cost,
                               np.max(np.abs(
                                   f_q.evaluate([cr.q_min, cr.q_max])))])

    if max_cost == 0:
        # Looks like we are facing loss minimization...
        if scenario.loss_price > 0:
            return 1 / (scenario.loss_price * scenario.base_mva)
        else:
            return 1.0

    max_inj = np.max([1,
                      np.max([np.abs([x.p_min, x.p_max,
                                      x.q_min, x.q_max]).max()
                              for x in cap]) / scenario.base_mva,
                      np.max([np.abs([x.real, x.imag]).max()
                              for x in load]) / scenario.base_mva
                      ])

    if max_cost > max_inj:
        return max_inj / max_cost
    return 1

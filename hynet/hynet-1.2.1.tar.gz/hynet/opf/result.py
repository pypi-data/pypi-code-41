"""
Representation of an optimal power flow result.
"""

import logging

import numpy as np

from hynet.types_ import SolverType, SolverStatus
from hynet.system.result import SystemResult
import hynet.config as config

_log = logging.getLogger(__name__)


class OPFResult(SystemResult):
    """
    Result of an optimal power flow calculation.

    **Remark:** In the data frames below, the respective column for the dual
    variables of a type of constraint (e.g., voltage drop) is only present if
    at least one constraint of this constraint type appears in the problem
    formulation.

    Parameters
    ----------
    model : OPFModel
        Model for the processed optimal power flow problem.
    empty : bool
        ``True`` if the object does not contain any result data and ``False``
        otherwise.
    solver : SolverInterface
        Solver object by which the result was obtained.
    solver_status : SolverStatus
        Status reported by the solver.
    solver_time : float
        Duration of the call to the solver in seconds.
    optimal_value : float
        Optimal objective value or ``numpy.nan`` if the solver failed.
    total_time : float or numpy.nan
        Total time for the OPF calculation, including the modeling, solving,
        and result assembly. If not provided, this time is set to ``numpy.nan``.
    reconstruction_mse : float
        Unavailable if the result is empty and, otherwise, the mean squared
        error of the reconstructed bus voltages in case of a relaxation and
        ``numpy.nan`` otherwise.

    bus : pandas.DataFrame, optional
        Unavailable if the result is empty and, otherwise, a data frame with
        the bus result data, indexed by the *bus ID*, which comprises the
        following columns:

        ``v``: (``hynet_complex_``)
            Bus voltage rms phasor (AC) or bus voltage magnitude (DC).
        ``s_shunt``: (``hynet_complex_``)
            Shunt apparent power in MVA. The real part constitutes the shunt
            losses in MW and the *negated* imaginary part constitutes the
            reactive power *injection*.
        ``bal_err``: (``hynet_complex_``)
            Power balance residual in MVA, i.e., the evaluation of the
            complex-valued power balance equation at the system state.
            Theoretically, this should be identical to zero, but due to a
            limited solver accuracy and/or inexactness of the relaxation it is
            only approximately zero. This residual supports the assessment of
            solution accuracy and validity.
        ``dv_bal_p``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power balance
            constraint in $/MW. In case of exactness of the relaxation (or
            zero duality gap in the QCQP), these dual variables equal the
            locational marginal prices (LMPs) for active power, cf. [1]_.
        ``dv_bal_q``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power balance
            constraint in $/Mvar. In case of exactness of the relaxation (or
            zero duality gap in the QCQP), these dual variables equal the
            locational marginal prices (LMPs) for reactive power, cf. [1]_.
        ``dv_v_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage lower bound in $/p.u..
        ``dv_v_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage upper bound in $/p.u..

    branch : pandas.DataFrame, optional
        Unavailable if the result is empty and, otherwise, a data frame with
        the branch result data, indexed by the *branch ID*, which comprises the
        following columns:

        ``s_src``: (``hynet_complex_``)
            Apparent power flow in MVA at the source bus (measured as a flow
            *into* the branch).
        ``s_dst``: (``hynet_complex_``)
            Apparent power flow in MVA at the destination bus (measured as a
            flow *into* the branch).
        ``i_src``: (``hynet_complex_``)
            Current flow in p.u. at the source bus (measured as a flow
            *into* the branch).
        ``i_dst``: (``hynet_complex_``)
            Current flow in p.u. at the destination bus (measured as a flow
            *into* the branch).
        ``v_drop``: (``hynet_float_``)
            Relative voltage magnitude drop from the source bus to the
            destination bus.
        ``angle_diff``: (``hynet_float_``)
            Bus voltage angle difference in degrees between the source and
            destination bus.
        ``effective_rating``: (``hynet_float_``)
            Ampacity in terms of a long-term MVA rating at the *actual* bus
            voltage. If no rating is available, it is set to ``numpy.nan``.
        ``rel_err``: (``hynet_float_``)
            Branch-related relative reconstruction error
            :math:`\\kappa_k(V^\\star)` as defined in equation (24) in [1]_ in
            case of a relaxed OPF or ``numpy.nan`` otherwise.
        ``dv_i_max_src``: (``hynet_float_``)
            Dual variable or KKT multiplier of the ampacity constraint at the
            source bus in $/p.u. or ``numpy.nan`` if unavailable.
        ``dv_i_max_dst``: (``hynet_float_``)
            Dual variable or KKT multiplier of the ampacity constraint at the
            destination bus in $/p.u. or ``numpy.nan`` if unavailable.
        ``dv_angle_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the angle difference lower bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_angle_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the angle difference upper bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_real_part``: (``hynet_float_``)
            Dual variable or KKT multiplier of the +/-90 degrees constraint
            on the angle difference (cf. equation (27) in [2]_) or
            ``numpy.nan`` if unavailable.
        ``dv_drop_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage drop lower bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_drop_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage drop upper bound
            constraint or ``numpy.nan`` if unavailable.

    converter : pandas.DataFrame
        Unavailable if the result is empty and, otherwise, a data frame with
        the converter result data, indexed by the *converter ID*, which
        comprises the following columns:

        ``p_src``: (``hynet_complex_``)
            Active power flow in MW at the source bus *into the converter*.
        ``p_dst``: (``hynet_complex_``)
            Active power flow in MW at the destination bus *into the
            converter*.
        ``q_src``: (``hynet_complex_``)
            Reactive power injection in Mvar at the source bus *into the grid*.
        ``q_dst``: (``hynet_complex_``)
            Reactive power injection in Mvar at the destination bus *into the
            grid*.
        ``loss_err``: (``hynet_float_``)
            Loss error in MW due to noncomplementary modes of the converter.
        ``loss_err_pre``: (``hynet_float_``)
            Only available if the OPF QCQP was pre-solved to detect and fix the
            converter modes. Loss error in MW in the pre-solution due to
            noncomplementary modes of the converter.
        ``dv_p_fwd_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the lower bound on the
            converter's forward mode active power flow in $/MW or ``numpy.nan``
            if unavailable.
        ``dv_p_fwd_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the upper bound on the
            converter's forward mode active power flow in $/MW or ``numpy.nan``
            if unavailable.
        ``dv_p_bwd_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the lower bound on the
            converter's backward mode active power flow in $/MW or ``numpy.nan``
            if unavailable.
        ``dv_p_bwd_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the upper bound on the
            converter's backward mode active power flow in $/MW or ``numpy.nan``
            if unavailable.
        ``dv_cap_src_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region at the source bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region at the source bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region at the destination bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region at the destination bus in $/Mvar or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_src_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            of the capability region at the source bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.
        ``dv_cap_dst_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            of the capability region at the destination bus in $/MVA or
            ``numpy.nan`` if unavailable.

    injector : pandas.DataFrame
        Unavailable if the result is empty and, otherwise, a data frame with
        the injector result data, indexed by the *injector ID*, which comprises
        the following columns:

        ``s``: (``hynet_complex_``)
            Apparent power injection in MVA.
        ``cost_p``: (``hynet_float_``)
            Cost of the active power injection in dollars or ``numpy.nan`` if
            no cost function was provided.
        ``cost_q``: (``hynet_float_``)
            Cost of the reactive power injection in dollars or ``numpy.nan`` if
            no cost function was provided.
        ``dv_cap_p_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power lower bound
            of the capability region in $/MW or ``numpy.nan`` if unavailable.
        ``dv_cap_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region in $/Mvar or ``numpy.nan`` if unavailable.
        ``dv_cap_p_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power upper bound
            of the capability region in $/MW or ``numpy.nan`` if unavailable.
        ``dv_cap_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region in $/Mvar or ``numpy.nan`` if unavailable.
        ``dv_cap_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.
        ``dv_cap_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.
        ``dv_cap_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.
        ``dv_cap_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            the capability region in $/MVA or ``numpy.nan`` if unavailable.

    References
    ----------
    .. [1] M. Hotz and W. Utschick, "The Hybrid Transmission Grid Architecture:
           Benefits in Nodal Pricing," in IEEE Trans. Power Systems, vol. 33,
           no. 2, pp. 1431-1442, Mar. 2018.
    .. [2] M. Hotz and W. Utschick, "A Hybrid Transmission Grid Architecture
           Enabling Efficient Optimal Power Flow," in IEEE Trans. Power
           Systems, vol. 31, no. 6, pp. 4504-4516, Nov. 2016.
    """

    def __init__(self, model, qcqp_result, total_time=np.nan, qcqp_result_pre=None):
        """
        Create an OPF result object.

        Parameters
        ----------
        model : hynet.opf.model.OPFModel
            Model for the processed OPF problem.
        qcqp_result : hynet.qcqp.result.QCQPResult
            Solution of the OPF QCQP.
        total_time : .hynet_float_, optional
            Total time for solving the OPF.
        qcqp_result_pre : QCQPResult, optional
            Pre-solution of the OPF QCQP for converter mode detection.
        """
        super().__init__(model,
                         qcqp_result,
                         total_time=total_time,
                         qcqp_result_pre=qcqp_result_pre)

        self._result_title = 'Optimal Power Flow'
        self._unit_dv_bal_p = '$/MWh'
        self._unit_dv_bal_q = '$/Mvarh'

    def __repr__(self):
        """Return a summary of the result."""
        t = ""
        t += self._get_header()
        t += "|> Data Source " + "-"*63 + "<|\n"
        t += "|" + " "*78 + "|\n"
        t += self._get_data_source_summary()
        t += "|" + " "*78 + "|\n"
        t += "|> Grid Information " + "-"*58 + "<|\n"
        t += "|" + " "*78 + "|\n"
        t += self._get_grid_structure_summary()
        t += "|" + " "*78 + "|\n"
        t += self._get_grid_injection_summary()
        t += "|" + " "*78 + "|\n"

        if not self.empty:
            t += "|> Results " + "-"*67 + "<|\n"
            t += "|" + " "*78 + "|\n"
            t += self._get_injection_and_loss_summary()
            t += "| Loss price:{:12.3f} $/MWh{:>13s}Loss penalty:{:14.3f} k$/h{:>4s}\n"\
                .format(self.scenario.loss_price,
                        "| ",
                        self.get_dynamic_losses() * self.scenario.loss_price / 1e3,
                        "|")
            t += "|" + " "*40 + "-+----+-" + " "*30 + "|\n"
            t += self._get_nodal_and_utilization_summary()
            t += "|" + " "*78 + "|\n"

        t += "|> Solution Process " + "-"*58 + "<|\n"
        t += "|" + " "*78 + "|\n"
        t += self._get_solver_info()
        t += self._get_solution_accuracy_info()
        t += self._get_pathological_price_profile_info()
        t += "+" + "-"*78 + "+\n"
        return t

    def _get_pathological_price_profile_info(self):
        t = ""
        if not (self.scenario.verify_hybrid_architecture_conditions(log=None) and
                self.solver_status == SolverStatus.SOLVED and
                self.solver.type != SolverType.QCQP and
                not self.has_valid_power_balance and
                self.reconstruction_mse >= 1e-8 and
                config.OPF['pathological_price_profile_info']):
            return t
        t += "|" + " "*78 + "|\n"
        t += "| This scenario exhibits a pathological price profile. Prominent causes are:   |\n"
        t += "|  (a) Zero marginal cost injectors: This can induce near-zero LMPs for        |\n"
        t += "|      active power. To add loss minimization, see Scenario.loss_price.        |\n"
        t += "|  (b) Shortage of inductive reactive power: This can induce negative LMPs     |\n"
        t += "|      for reactive power. To add compensation, see Scenario.add_compensation. |\n"
        t += "| To analyze the cause of inexactness, see hynet.show_power_balance_error.     |\n"
        t += "| In some cases, Scenario.set_minimum_series_resistance may be supportive.     |\n"
        return t


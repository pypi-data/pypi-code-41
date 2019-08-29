"""
Representation of a maximum loadability result.
"""

import logging

import numpy as np

from hynet.types_ import BranchType
from hynet.system.result import SystemResult

_log = logging.getLogger(__name__)


class LoadabilityResult(SystemResult):
    """
    Result of a maximum loadability calculation.

    **Remark:** In the data frames below, the respective column for the dual
    variables of a type of constraint (e.g., voltage drop) is only present if
    at least one constraint of this constraint type appears in the problem
    formulation.

    Parameters
    ----------
    model : LoadabilityModel
        Model for the processed maximum loadability problem.
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
        Total time for the loadability calculation, including the modeling,
        solving, and result assembly. If not provided, this time is set to
        ``numpy.nan``.
    reconstruction_mse : float
        Unavailable if the result is empty and, otherwise, the mean squared
        error of the reconstructed bus voltages in case of a relaxation and
        ``numpy.nan`` otherwise.
    load_increment_scaling : float
        Maximum load increment scaling (cf. :math:`\\lambda` in equation (1)
        and (2) in [1]_) or ``numpy.nan`` if the solver failed.

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
            constraint.
        ``dv_bal_q``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power balance
            constraint.
        ``dv_v_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage lower bound.
        ``dv_v_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the voltage upper bound.

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
            :math:`\\kappa_k(V^\\star)` as defined in equation (24) in [2]_ in
            case of a relaxed QCQP or ``numpy.nan`` otherwise.
        ``dv_i_max_src``: (``hynet_float_``)
            Dual variable or KKT multiplier of the ampacity constraint at the
            source bus or ``numpy.nan`` if unavailable.
        ``dv_i_max_dst``: (``hynet_float_``)
            Dual variable or KKT multiplier of the ampacity constraint at the
            destination bus or ``numpy.nan`` if unavailable.
        ``dv_angle_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the angle difference lower bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_angle_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the angle difference upper bound
            constraint or ``numpy.nan`` if unavailable.
        ``dv_real_part``: (``hynet_float_``)
            Dual variable or KKT multiplier of the +/-90 degrees constraint
            on the angle difference (cf. equation (27) in [3]_) or
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

        ``p_src``: (``hynet_float_``)
            Active power flow in MW at the source bus *into the converter*.
        ``p_dst``: (``hynet_float_``)
            Active power flow in MW at the destination bus *into the
            converter*.
        ``q_src``: (``hynet_float_``)
            Reactive power injection in Mvar at the source bus *into the grid*.
        ``q_dst``: (``hynet_float_``)
            Reactive power injection in Mvar at the destination bus *into the
            grid*.
        ``loss_err``: (``hynet_float_``)
            Loss error in MW due to noncomplementary modes of the converter.
        ``loss_err_pre``: (``hynet_float_``)
            Only available if the QCQP was pre-solved to detect and fix the
            converter modes. Loss error in MW in the pre-solution due to
            noncomplementary modes of the converter.
        ``dv_p_fwd_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the lower bound on the
            converter's forward mode active power flow or ``numpy.nan`` if
            unavailable.
        ``dv_p_fwd_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the upper bound on the
            converter's forward mode active power flow or ``numpy.nan`` if
            unavailable.
        ``dv_p_bwd_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the lower bound on the
            converter's backward mode active power flow or ``numpy.nan`` if
            unavailable.
        ``dv_p_bwd_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the upper bound on the
            converter's backward mode active power flow or ``numpy.nan`` if
            unavailable.
        ``dv_cap_src_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region at the source bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_src_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region at the source bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_dst_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region at the destination bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_dst_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region at the destination bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_src_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            of the capability region at the source bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_src_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            of the capability region at the source bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_src_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            of the capability region at the source bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_src_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            of the capability region at the source bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_dst_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            of the capability region at the destination bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_dst_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            of the capability region at the destination bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_dst_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            of the capability region at the destination bus or ``numpy.nan`` if
            unavailable.
        ``dv_cap_dst_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            of the capability region at the destination bus or ``numpy.nan`` if
            unavailable.

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
            of the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_q_min``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power lower bound
            of the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_p_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the active power upper bound
            of the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_q_max``: (``hynet_float_``)
            Dual variable or KKT multiplier of the reactive power upper bound
            of the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_lt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-top half-space of
            the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_rt``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-top half-space of
            the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_lb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the left-bottom half-space of
            the capability region or ``numpy.nan`` if unavailable.
        ``dv_cap_rb``: (``hynet_float_``)
            Dual variable or KKT multiplier of the right-bottom half-space of
            the capability region or ``numpy.nan`` if unavailable.

    References
    ----------
    .. [1] G. D. Irisarri, X. Wang, J. Tong and S. Mokhtari, "Maximum
           loadability of power systems using interior point nonlinear
           optimization method," IEEE Trans. Power Syst., vol. 12, no. 1,
           pp. 162-172, Feb. 1997.
    .. [2] M. Hotz and W. Utschick, "The Hybrid Transmission Grid Architecture:
           Benefits in Nodal Pricing," in IEEE Trans. Power Systems, vol. 33,
           no. 2, pp. 1431-1442, Mar. 2018.
    .. [3] M. Hotz and W. Utschick, "A Hybrid Transmission Grid Architecture
           Enabling Efficient Optimal Power Flow," in IEEE Trans. Power
           Systems, vol. 31, no. 6, pp. 4504-4516, Nov. 2016.
    """

    def __init__(self, model, qcqp_result, total_time=np.nan, qcqp_result_pre=None):
        """
        Create a loadability result object.

        Parameters
        ----------
        model : hynet.loadability.model.LoadabilityModel
            Model for the processed loadability problem.
        qcqp_result : hynet.qcqp.result.QCQPResult
            Solution of the loadability-QCQP.
        total_time : .hynet_float_, optional
            Total time for solving the loadability problem.
        qcqp_result_pre : QCQPResult, optional
            Pre-solution of the loadability QCQP for converter mode detection.
        """
        # Set the scenario with the scaled load prior to the initialization of
        # the base class such that, with the overridden property ``scenario``,
        # the base class utilizes the updated scenario.
        self._scenario_scaled = model.scenario.copy()
        if not qcqp_result.empty:
            self.load_increment_scaling = qcqp_result.optimizer.z[0]
            self._scenario_scaled.bus['load'] += \
                self.load_increment_scaling \
                * self._scenario_scaled.bus['load_increment']
        else:
            self.load_increment_scaling = np.nan

        # Initialization of the base class
        super().__init__(model,
                         qcqp_result,
                         total_time=total_time,
                         qcqp_result_pre=qcqp_result_pre)

        # Set the title for this result
        self._result_title = 'Maximum Loadability'

    @property
    def scenario(self):
        """Return the scenario with the identified *maximum load*."""
        return self._scenario_scaled

    @property
    def original_scenario(self):
        """Return the original scenario data."""
        return self.model.scenario

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
            t += self._get_loadability_summary()
            t += "|" + " "*39 + "--+--" + " "*34 + "|\n"
            t += self._get_injection_and_loss_summary()
            t += "|" + " "*41 + "|" + " "*36 + "|\n"
            t += self._get_nodal_and_utilization_summary()
            t += "|" + " "*78 + "|\n"

        t += "|> Solution Process " + "-"*58 + "<|\n"
        t += "|" + " "*78 + "|\n"
        t += self._get_solver_info()
        t += self._get_solution_accuracy_info()
        t += "+" + "-"*78 + "+\n"
        return t

    def _get_grid_injection_summary(self):
        """
        This method is overridden to report the load of the original scenario.
        """
        injector = self.original_scenario.injector
        total_load = self.original_scenario.bus['load'].sum()

        t = ""
        t += "| Injection:{:11.1f} MW{:>10s} Mvar | Min.:{:9.1f} MW /{:10.1f} Mvar |\n"\
            .format(sum(x.p_max for x in injector['cap']),
                    "/{:8.1f}".format(sum(x.q_max for x in injector['cap'])),
                    sum(x.p_min for x in injector['cap']),
                    sum(x.q_min for x in injector['cap']))
        t += "| Total load:{:10.1f} MW /{:8.1f} Mvar | Loading:{:8.2%} of P-capacity     |\n"\
            .format(total_load.real, total_load.imag,
                    self.original_scenario.get_relative_loading())
        return t

    def _get_loadability_summary(self):
        bus = self.scenario.bus
        injector = self.scenario.injector

        p_capacity = sum(x.p_max for x in injector['cap'])
        p_tot_load = bus['load'].to_numpy().real.sum()

        total_load_increment = bus['load_increment'].sum()

        t = ""
        t += "| Max. load:{:11.1f} MW /{:8.1f} Mvar | Loading:{:19.2%} P-cap. |\n"\
            .format(p_tot_load,
                    bus['load'].to_numpy().imag.sum(),
                    p_tot_load/p_capacity)
        t += "| Increment:{:11.1f} MW /{:8.1f} Mvar | Load increase:{:13.2%} Incre. |\n"\
            .format(total_load_increment.real,
                    total_load_increment.imag,
                    self.load_increment_scaling)
        return t

    def _get_nodal_and_utilization_summary(self):
        v_abs = np.abs(self.bus['v'])
        v_angle = np.angle(self.bus['v']) * 180/np.pi

        branch_utilization = self.get_branch_utilization()

        branch_type = self.scenario.branch['type']
        util_line = branch_utilization[branch_type == BranchType.LINE].mean()
        util_tf = branch_utilization[branch_type == BranchType.TRANSFORMER].mean()

        t = ""
        t += "| Voltage mag.:{:10.3f} to{:8.3f} p.u. | Line util.:       {:<17s}|\n"\
            .format(v_abs.min(),
                    v_abs.max(),
                    "{:9.2%} (mean)".format(util_line) if not np.isnan(util_line)
                    else "     -")
        t += "| Voltage angle:{:8.2f}  to{:7.2f} deg.  | Transformer util.:{:<17s}|\n"\
            .format(v_angle.min(),
                    v_angle.max(),
                    "{:9.2%} (mean)".format(util_tf) if not np.isnan(util_tf)
                    else "     -")
        return t

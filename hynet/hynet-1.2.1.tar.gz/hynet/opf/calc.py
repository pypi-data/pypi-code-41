"""
Calculation of the optimal power flow.
"""

import logging

from hynet.types_ import SolverType
from hynet.solver import AVAILABLE_SOLVERS
from hynet.data.connection import DBConnection
from hynet.data.interface import load_scenario
from hynet.scenario.representation import Scenario
from hynet.opf.model import OPFModel
from hynet.opf.result import OPFResult
from hynet.opf.initial_point import CopperPlateInitialPointGenerator
from hynet.system.calc import calc

_log = logging.getLogger(__name__)


def get_default_initial_point_generator():
    """
    Return the default initial point generator for the current system.

    If a sufficiently efficient SOCR solver is available, the utilization of a
    copper plate based initial point for the solution of the nonconvex QCQP
    typically improves the overall performance, i.e., that the reduced number
    of iterations of the QCQP solver outweighs the computational cost for the
    initial point.
    """
    socr_solvers = [x for x in AVAILABLE_SOLVERS if x().type == SolverType.SOCR]

    def find_solver(solver_name):
        for SolverClass in socr_solvers:
            if SolverClass().name == solver_name:
                return SolverClass
        return None

    # Prioritized search for a suitable SOCR solver
    for solver_name in ['MOSEK', 'CPLEX']:
        SolverClass = find_solver(solver_name)
        if SolverClass is not None:
            return CopperPlateInitialPointGenerator(SolverClass())
    return None


def calc_opf(data, scenario_id=0, solver=None, solver_type=SolverType.QCQP,
             initial_point_generator=get_default_initial_point_generator(),
             converter_loss_error_tolerance=5e-4):
    """
    Calculate the optimal power flow.

    This function formulates and solves the optimal power flow (OPF) problem.
    The solver or solver type may be specified explicitly, otherwise an
    appropriate solver is selected automatically.

    Parameters
    ----------
    data : DBConnection or Scenario or OPFModel
        Connection to a *hynet* grid database, a ``Scenario`` object, or a
        ``OPFModel`` object.
    scenario_id : .hynet_id_, optional
        Identifier of the scenario. This argument is ignored if ``data`` is a
        ``Scenario`` or ``OPFModel`` object.
    solver : SolverInterface, optional
        Solver for the QCQP problem; the default automatically selects an
        appropriate solver of the specified solver type.
    solver_type : SolverType, optional
        Solver type for the automatic solver selection (default
        ``SolverType.QCQP``). It is ignored if ``solver`` is not ``None``.
    initial_point_generator : InitialPointGenerator or None, optional
        Initial point generator for QCQP solvers (ignored for relaxation-based
        solvers). By default, an appropriate initial point generator is
        selected if a computationally efficient SOCR solver is installed.
        Set to ``None`` to skip the initial point generation.
    converter_loss_error_tolerance : .hynet_float_, optional
        Tolerance for the converter loss error in MW (default ``5e-4``). If
        ``None``, the OPF model's (default) setting is retained.

    Returns
    -------
    result : OPFResult
        Optimal power flow solution.

    See Also
    --------
    hynet.scenario.representation.Scenario
    hynet.opf.result.OPFResult
    hynet.reduction.copper_plate.reduce_to_copper_plate
    hynet.opf.initial_point : Initial point generators.
    """
    if isinstance(data, OPFModel):
        model = data
    elif isinstance(data, Scenario):
        model = OPFModel(data)
    elif isinstance(data, DBConnection):
        model = OPFModel(load_scenario(data, scenario_id))
    else:
        raise ValueError(("The argument 'data' must be DBConnection object, "
                          "a Scenario object, or an OPFModel object."))

    if converter_loss_error_tolerance is not None:
        model.converter_loss_error_tolerance = converter_loss_error_tolerance

    return calc(model,
                solver=solver,
                solver_type=solver_type,
                initial_point_generator=initial_point_generator)

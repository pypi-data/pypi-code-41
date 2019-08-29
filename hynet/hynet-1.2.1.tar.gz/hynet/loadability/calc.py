"""
Calculation of the maximum loadability.
"""

import logging

from hynet.types_ import SolverType
from hynet.data.connection import DBConnection
from hynet.data.interface import load_scenario
from hynet.scenario.representation import Scenario
from hynet.loadability.model import LoadabilityModel
from hynet.loadability.result import LoadabilityResult
from hynet.system.calc import calc

_log = logging.getLogger(__name__)


def calc_loadability(data, scenario_id=0, solver=None,
                     solver_type=SolverType.QCQP, initial_point_generator=None,
                     converter_loss_error_tolerance=5e-4):
    """
    Calculate the maximum loadability.

    This function formulates and solves the maximum loadability problem as
    defined in equations (1) - (3) in [1]_ based on the feasibility set of the
    OPF problem in *hynet*, i.e., *hynet*'s the power balance equations are
    extended with a scaled load increment and the scaling of the increment is
    maximized. The nodal load increment is defined by the column
    ``'load_increment'`` in the ``bus`` data frame of the scenario. If this
    column is not present, the load increment is set to the nodal load (i.e.,
    the ``'load'`` column of the ``bus`` data frame), which maintains a
    constant power factor at the loads.

    Parameters
    ----------
    data : DBConnection or Scenario or LoadabilityModel
        Connection to a *hynet* grid database, a ``Scenario`` object, or a
        ``LoadabilityModel`` object.
    scenario_id : .hynet_id_, optional
        Identifier of the scenario. This argument is ignored if ``data`` is a
        ``Scenario`` or ``LoadabilityModel`` object.
    solver : SolverInterface, optional
        Solver for the QCQP problem; the default automatically selects an
        appropriate solver of the specified solver type.
    solver_type : SolverType, optional
        Solver type for the automatic solver selection (default
        ``SolverType.QCQP``). It is ignored if ``solver`` is not ``None``.
    initial_point_generator : InitialPointGenerator or None, optional
        Initial point generator for QCQP solvers (ignored for relaxation-based
        solvers). By default (``None``), the initial point generation is
        skipped.
    converter_loss_error_tolerance : .hynet_float_, optional
        Tolerance for the converter loss error in MW (default ``5e-4``). If
        ``None``, the loadability model's (default) setting is retained.

    Returns
    -------
    result : LoadabilityResult
        Solution of the maximum loadability problem.

    See Also
    --------
    hynet.scenario.representation.Scenario
    hynet.loadability.result.LoadabilityResult

    References
    ----------
    .. [1] G. D. Irisarri, X. Wang, J. Tong and S. Mokhtari, "Maximum
           loadability of power systems using interior point nonlinear
           optimization method," IEEE Trans. Power Syst., vol. 12, no. 1,
           pp. 162-172, Feb. 1997.
    """
    if isinstance(data, LoadabilityModel):
        model = data
    elif isinstance(data, Scenario):
        model = LoadabilityModel(data)
    elif isinstance(data, DBConnection):
        model = LoadabilityModel(load_scenario(data, scenario_id))
    else:
        raise ValueError(("The argument 'data' must be DBConnection object, "
                          "a Scenario object, or a LoadabilityModel object."))

    if converter_loss_error_tolerance is not None:
        model.converter_loss_error_tolerance = converter_loss_error_tolerance

    return calc(model,
                solver=solver,
                solver_type=solver_type,
                initial_point_generator=initial_point_generator)

"""
Calculate the solution of an optimization problem specified by a given model.
"""

import logging

from hynet.types_ import SolverType
from hynet.solver import AVAILABLE_SOLVERS
from hynet.opf.model import SystemModel
from hynet.qcqp.solver import SolverInterface
from hynet.utilities.base import Timer

_log = logging.getLogger(__name__)


def calc(model, solver=None, solver_type=SolverType.QCQP,
         initial_point_generator=None):
    """
    Calculate the solution of the optimization problem for the given model.

    Model classes take the scenario data to build a specific optimization
    problem. This function takes the model to generate the specification of
    the optimization problem, solve the problem using the specified solver,
    and route the result data though the model object to generate and
    return an appropriate result object. The solver or solver type may be
    specified explicitly, otherwise an appropriate solver is selected
    automatically.

    Parameters
    ----------
    model : SystemModel
        Model object that generates the quadratically constrained quadratic
        problem (QCQP).
    solver : SolverInterface, optional
        Solver for the QCQP problem; the default automatically selects an
        appropriate solver of the specified solver type.
    solver_type : SolverType, optional
        Solver type for the automatic solver selection (default
        ``SolverType.QCQP``). It is ignored if ``solver`` is not ``None``.
    initial_point_generator : InitialPointGenerator or None, optional
        Initial point generator for QCQP solvers (ignored for relaxation-based
        solvers). If ``None`` (default), the initial point generation is
        skipped.

    Returns
    -------
    result : SystemResult
        Result data of the solution of the optimization problem.

    See Also
    --------
    hynet.system.model.SystemModel
    hynet.system.result.SystemResult
    hynet.system.initial_point : Initial point generators.
    """
    timer = Timer()
    if not isinstance(model, SystemModel):
        raise ValueError("The model must be a SystemModel-derived object.")

    if solver is None:
        solver = select_solver(solver_type)()
    elif not isinstance(solver, SolverInterface):
        raise ValueError("The solver must be a SolverInterface-derived object.")

    qcqp = model.get_problem()

    if solver.type == SolverType.QCQP and initial_point_generator is not None:
        qcqp.initial_point = initial_point_generator(model, qcqp)

    _log.debug("QCQP creation ({:.3f} sec.)".format(timer.interval()))

    result = solver.solve(qcqp)

    if not result.empty and \
            not model.verify_converter_loss_accuracy(result.optimizer):
        _log.debug("Converter loss error exceeds the tolerance. "
                   "Solving the QCQP with fixed modes based on the net flow.")
        model.fix_converter_modes(qcqp, result.optimizer)
        result_pre = result
        result = solver.solve(qcqp)
    else:
        result_pre = None

    return model.create_result(result,
                               total_time=timer.total(),
                               qcqp_result_pre=result_pre)


def select_solver(solver_type):
    """
    Return the most appropriate installed solver of the specified solver type.

    Parameters
    ----------
    solver_type : SolverType
        Specification of the solver type.

    Returns
    -------
    solver : SolverInterface
        Selected solver interface *class* of the specified solver type.

    Raises
    ------
    RuntimeError
        In case no appropriate solver was found.
    """
    solver_classes = list(filter(lambda x: x().type == solver_type,
                                 AVAILABLE_SOLVERS))

    if not solver_classes:
        raise RuntimeError("No supported {:s} solver was found."
                           .format(solver_type.name))

    return solver_classes[0]

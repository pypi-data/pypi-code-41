import numpy as np

from pySDC.helpers.stats_helper import filter_stats, sort_stats
from pySDC.implementations.collocation_classes.gauss_radau_right import CollGaussRadau_Right
from pySDC.implementations.controller_classes.controller_nonMPI import controller_nonMPI
from pySDC.implementations.problem_classes.HeatEquation_ND_FD_forced_periodic import heatNd_periodic
from pySDC.implementations.sweeper_classes.imex_1st_order import imex_1st_order
from pySDC.playgrounds.compression.HookClass_iteration_estimator import iteration_estimator


def setup(dt=None, ndim=None):

    # initialize level parameters
    level_params = dict()
    level_params['restol'] = 1E-12
    level_params['dt'] = dt  # time-step size
    level_params['nsweeps'] = 1

    # initialize sweeper parameters
    sweeper_params = dict()
    sweeper_params['collocation_class'] = CollGaussRadau_Right
    sweeper_params['num_nodes'] = 7
    sweeper_params['QI'] = ['LU']  # For the IMEX sweeper, the LU-trick can be activated for the implicit part
    # sweeper_params['initial_guess'] = 'zero'

    # initialize problem parameters
    problem_params = dict()
    problem_params['ndim'] = ndim  # will be iterated over
    problem_params['order'] = 8  # will be iterated over
    problem_params['nu'] = 1.0  # diffusion coefficient
    problem_params['freq'] = tuple(2 for _ in range(ndim))  # frequencies
    problem_params['nvars'] = tuple(32 for _ in range(ndim))  # number of dofs
    problem_params['direct_solver'] = True

    # initialize step parameters
    step_params = dict()
    step_params['maxiter'] = 50

    # initialize controller parameters
    controller_params = dict()
    controller_params['logger_level'] = 20
    controller_params['hook_class'] = iteration_estimator

    # fill description dictionary for easy step instantiation
    description = dict()
    description['problem_class'] = heatNd_periodic  # pass problem class
    description['problem_params'] = problem_params  # pass problem parameters
    description['sweeper_class'] = imex_1st_order  # pass sweeper (see part B)
    description['sweeper_params'] = sweeper_params  # pass sweeper parameters
    description['level_params'] = level_params  # pass level parameters
    description['step_params'] = step_params  # pass step parameters

    return description, controller_params


def run_reference():
    """
    A simple test program to do SDC runs for the heat equation in various dimensions
    """

    # set time parameters
    t0 = 0.0
    Tend = 1E-01

    dt = 1E-01
    ndim = 1

    print(f'Working on {ndim} dimensions with time-step size {dt}...')

    description, controller_params = setup(dt, ndim)

    # instantiate controller
    controller = controller_nonMPI(num_procs=1, controller_params=controller_params, description=description)

    # get initial values on finest level
    P = controller.MS[0].levels[0].prob
    uinit = P.u_exact(t0)

    # call main function to get things done...
    uend, stats = controller.run(u0=uinit, t0=t0, Tend=Tend)

    # filter statistics by type (number of iterations)
    iter_counts = sort_stats(filter_stats(stats, type='niter'), sortby='time')

    niters = np.array([item[1] for item in iter_counts])
    out = f'   Mean number of iterations: {np.mean(niters):4.2f}'
    print(out)

    # filter statistics by type (error after time-step)
    errors = sort_stats(filter_stats(stats, type='error_after_step'), sortby='time')
    out = f'   Error after step {errors[-1][0]:8.4f}: {errors[-1][1]:8.4e}'
    print(out)

    # filter statistics by type (error after time-step)
    timing = sort_stats(filter_stats(stats, type='timing_run'), sortby='time')
    out = f'...done, took {timing[0][1]} seconds!'
    print(out)

    print()


if __name__ == "__main__":
    run_reference()

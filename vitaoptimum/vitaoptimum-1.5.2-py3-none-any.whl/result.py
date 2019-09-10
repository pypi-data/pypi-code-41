import sys
import numpy as np
from abc import abstractmethod

import vitaoptimum.plot as plot


##############################################################################
#                      ALGORITHMS RESULT MAIN BASE CLASS                     #
##############################################################################

class _ResultBase:

    @abstractmethod
    def to_string(self, separator):
        pass

    @abstractmethod
    def plot_convergence(self, title, logo, save_to):
        pass

    def __str__(self):
        return self.to_string(separator="\n")

    def _print_quality(self, separator):
        lines = [
            "",
            "Quality Measures:",
            "Delta: ".rjust(14, ' ') + str(self._quality[0]),
            "Diameter: ".rjust(14, ' ') + str(self._quality[1]),
            "Deviation: ".rjust(14, ' ') + str(self._quality[2]),
            "Evaluation: ".rjust(14, ' ') + str(int(self._quality[3])),
        ]
        return separator.join(lines)

    def print(self, device=sys.stdout):
        ''' Print found solution details'''
        if device:
            device.write(self.to_string(separator="\n"))
            device.write("\n")
        else:
            print(sys.stderr, "Print device is not defined")

    def plot_function(self, sol_range=None, dim_indices=None,
                      title='Function', logo=True, save_to=None):
        ''' Plot objective function'''
        if self._dim <= 0:
            print(sys.stderr, "Problem's dimenstion is unknown: can't plot function")
            return False

        if not sol_range:
            if self._low == []:
                print(sys.stderr, "Range low value is not set")
                return False
            if self._high == []:
                print(sys.stderr, "Range high value is not set")
                return False
            sol_range = [self._low, self._high]

        if self._dim == 1:
            if not isinstance(sol_range, list):
                print(sys.stderr, "Range must be a list: [low, high]")
                return False
            elif len(sol_range) != 2:
                print(sys.stderr, "Range list size must be 2: [low, high]")
                return False
            else:
                print("Plot 1d function for range: %s" % sol_range)
                plot.fobj_1d(self._fobj, sol_range, title, logo, save_to)

        else:
            if not isinstance(sol_range, list):
                print(sys.stderr, "Range must be a list: [[low0, high0], [low1, high1]]")
                return False
            elif len(sol_range) != 2:
                print(sys.stderr, "Range list size must be 2: [[low0, high0], [low1, high1]]")
                return False
            else:
                print("Plot 2d function for range: %s" % sol_range)
                if not dim_indices:
                    dim_indices = [0, 1]
                low0  = sol_range[0][dim_indices[0]]
                high0 = sol_range[1][dim_indices[0]]
                low1  = sol_range[0][dim_indices[1]]
                high1 = sol_range[1][dim_indices[1]]
                if low0 == high0:
                    print("Low and high boundaries (low[0] and high[0]) must differ: %d" % low0)
                    return False
                if low1 == high1:
                    print("Low and high boundaries (low[1] and high[1]) must differ: %d" % low1)
                    return False
                plot.fobj_2d(self._fobj, self._solution, [low0, high0], [low1, high1],
                             self._dim, dim_indices, title, logo, save_to)
        return True

    def plot_optimum(self, title='Optimum', eps=0.01,
                     dim_indices=None, logo=True, save_to=None):
        ''' Plot optimum of found solution'''
        if self._dim <= 0:
            print(sys.stderr, "Problem dimenstion is unknown: can't plot optimum")
            return False

        sol_range = None
        if self._dim == 1:
            if len(self._low) == 1 and len(self._high) == 1:
                sol_range = [self._low[0], self._high[0]]
            print("Plot 1d optimum in boundaries %s" % sol_range)
            plot.optimum_1d(title, self._fobj, self._solution,
                            sol_range, eps, logo, save_to)
        else:
            if len(self._low) and len(self._high):
                sol_range = [self._low, self._high]
            print("Plot 2d optimum in boundaries %s" % sol_range)
            plot.optimum_2d(title, self._fobj, self._solution, sol_range, eps,
                            self._dim, dim_indices, logo, save_to)
        return True


##############################################################################
#                      VITA OPTIMUM RESULTS BASE CLASSES                     #
##############################################################################


class _VitaOptimumResult(_ResultBase):
    """Base result for all VitaOptimum Methods"""

    def __init__(self, dim, fobj,
                 best_fobj, solution, convergence):
        self._low = []
        self._high = []
        self._dim = dim
        self._fobj = fobj
        self._best_fobj = best_fobj
        self._solution = solution
        self._convergence = convergence

    def to_string(self, separator='\n'):
        np.set_printoptions(precision=20)
        lines = [
            f"Best function: {self._best_fobj}",
            f"Best solution: {self._solution}",
            f"Convergence:\n {self._convergence}",
        ]
        return separator.join(lines)

    def plot_convergence(self, title='Convergence', logo=True, save_to=None):
        '''Plot convergence of the solution search by VitaOptimum'''
        plot.convergence(self._convergence, title, logo, save_to)

    @property
    def solution(self):
        return self._solution

    @property
    def best_fobj(self):
        return self._best_fobj

    @property
    def convergence(self):
        return self._convergence


class _VitaOptimumUnconstrainedResult(_VitaOptimumResult):
    """Base result for all VitaOptimum Unconstrained Methods"""

    def to_string(self, separator='\n'):
        lines = [super().to_string(separator)]
        return separator.join(lines)


class _VitaOptimumConstrainedResult(_VitaOptimumResult):
    """Base result for all VitaOptimum Constrained Methods"""

    def __init__(self, dim, fobj, best_fobj, solution, best_constrains, convergence):
        self._best_constrains = best_constrains
        _VitaOptimumResult.__init__(self, dim, fobj, best_fobj, solution, convergence)

    def to_string(self, separator='\n'):
        lines = [super().to_string(separator)]
        lines.append(f"Best constraint values: {self._best_constrains}")
        return separator.join(lines)

    @property
    def constrains(self):
        return self._best_constrains


class _VitaOptimumMixedResult(_VitaOptimumResult):
    """Mixed Unonstrained Method Result"""

    def __init__(self, dim, fobj, best_fobj, continuous_solution, integer_solution,
                 binary_solution, permutations_solution, convergence):
        mixed_solution = [
            continuous_solution,
            integer_solution,
            binary_solution,
            permutations_solution
        ]
        _VitaOptimumUnconstrainedResult.__init__(self, dim, fobj, best_fobj,
                                                 mixed_solution, convergence)

    def to_string(self, separator='\n'):
        lines = [
            f"Best function: {self._best_fobj}",
            f"Found continuous solution: {self._solution[0]}",
            f"Found integer solution: {self._solution[1]}",
            f"Found binary solution: {self._solution[2]}",
            f"Found permutations solution: {self._solution[3]}",
            f"Convergence:\n {self._convergence}",
        ]
        return separator.join(lines)


##############################################################################
#                            VITA OPTIMUM RESULTS                            #
##############################################################################

class VitaOptimumBcsResult(_VitaOptimumConstrainedResult):
    """Binary Constrained Method Result"""

    def to_string(self, separator='\n'):
        lines = [
            f"Binary Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumBusResult(_VitaOptimumUnconstrainedResult):
    """Binary Unconstrained Global Optimization Method Result"""

    def to_string(self, separator='\n'):
        lines = [
            f"Binary Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumCcsResult(_VitaOptimumConstrainedResult):
    """Continuous Constrained Method Result"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 solution, best_constrains, convergence):
        _VitaOptimumConstrainedResult.__init__(self, dim, fobj, best_fobj,
                                               solution, best_constrains, convergence)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Continuous Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumCusResult(_VitaOptimumUnconstrainedResult):
    """Continuous Unconstrained Method Result"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 solution, convergence):
        _VitaOptimumResult.__init__(self, dim, fobj, best_fobj, solution, convergence)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Continuous Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumIcsResult(_VitaOptimumConstrainedResult):
    """Integer Constrained Method Result"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 solution, best_constrains, convergence):
        self._best_constrains = best_constrains
        _VitaOptimumResult.__init__(self, dim, fobj, best_fobj, solution, convergence)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Integer Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumIusResult(_VitaOptimumUnconstrainedResult):
    """Integer Unconstrained Method Result"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 solution, convergence):
        _VitaOptimumUnconstrainedResult.__init__(self, dim, fobj, best_fobj,
                                                 solution, convergence)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Integer Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumMcsResult(_VitaOptimumConstrainedResult):
    """Mixed Constrained Method Result"""

    def __init__(self, fobj, best_fobj, continuous_solution, integer_solution,
                 binary_solution, permutations_solution, best_constrains,
                 convergence):
        self._dim = 0
        self._best_constrains = best_constrains
        _VitaOptimumMixedResult.__init__(
            self, self._dim, fobj, best_fobj, continuous_solution,
            integer_solution, binary_solution,
            permutations_solution, convergence)

    @property
    def best_constrains(self):
        return self._best_constrains

    def to_string(self, separator='\n'):
        lines = [
            f"Mixed Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        lines.append(f"Best constraint values: {self._best_constrains}")
        return separator.join(lines)


class VitaOptimumMusResult(_VitaOptimumUnconstrainedResult):
    """Mixed Unconstrained Method Result"""

    def __init__(self, fobj, best_fobj, continuous_solution, integer_solution,
                 binary_solution, permutations_solution, convergence):
        self._dim = 0
        _VitaOptimumMixedResult.__init__(
            self, self._dim, fobj, best_fobj, continuous_solution,
            integer_solution, binary_solution,
            permutations_solution, convergence)

    def to_string(self, separator='\n'):
        lines = [
            f"Mixed Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPcsResult(_VitaOptimumConstrainedResult):
    """Permutation Constrained Method Result"""

    def to_string(self, separator='\n'):
        lines = [
            f"Permutation Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPusResult(_VitaOptimumUnconstrainedResult):
    """Permutation Unconstrained Method Result"""

    def to_string(self, separator='\n'):
        lines = [
            f"Permutation Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


##############################################################################
#                            VITA OPTIMUM PLUS RESULTS                       #
##############################################################################

class _VitaOptimumPlusResult(_ResultBase):
    """Base result for all VitaOptimum Plus Global Optimization Methods"""

    def __init__(self, dim, fobj, best_fobj,
                 solution, is_converged, quality):
        self._low = []
        self._high = []
        self._dim = dim
        self._fobj = fobj
        self._best_fobj = best_fobj
        self._solution = solution
        self._is_converged = is_converged
        self._quality = quality

    def to_string(self, separator='\n'):
        lines = [
            f"Is converged: {self._is_converged[0]}",
            "",
            f"Best function: {self._best_fobj}",
            f"Best solution: {self._solution[0]}",
        ]
        lines.append(self._print_quality(separator))
        return separator.join(lines)

    def plot_convergence(self, title, logo=True, save_to=None):
        '''Plot convergence of the solution search by VitaOptimum Plus'''
        print("Not implemented")

    @property
    def solution(self):
        return self._solution

    @property
    def quality(self):
        return self._quality

    @property
    def best_fobj(self):
        return self._best_fobj

    @property
    def is_converged(self):
        return self._is_converged


class _VitaOptimumPlusConstrainedResult(_VitaOptimumPlusResult):

    def __init__(self, dim, fobj, best_fobj, best_constrains,
                 solution, is_converged, quality):
        self._best_constrains = best_constrains
        _VitaOptimumPlusResult.__init__(self, dim, fobj, best_fobj,
                                        solution, is_converged, quality)

    @property
    def best_constrains(self):
        return self._best_constrains

    def to_string(self, separator='\n'):
        lines = [super().to_string(separator)]
        lines.append(f"Best constraint values: {self._best_constrains}")
        return separator.join(lines)


class _VitaOptimumPlusUnconstrainedResult(_VitaOptimumPlusResult):

    def to_string(self, separator='\n'):
        lines = [super().to_string(separator)]
        return separator.join(lines)


class VitaOptimumPlusBcsResult(_VitaOptimumPlusConstrainedResult):
    """Binary Constrained Method Result (VO+)"""

    def to_string(self, separator='\n'):
        lines = [
            f"Binary Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusBusResult(_VitaOptimumPlusUnconstrainedResult):
    """Binary Unconstrained Method Result (VO+)"""

    def to_string(self, separator='\n'):
        lines = [
            f"Binary Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusCcsResult(_VitaOptimumPlusConstrainedResult):
    """Continuous Constrained Method Result (VO+)"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 best_constrains, solution, is_converged, quality):
        _VitaOptimumPlusConstrainedResult.__init__(
            self, dim, fobj, best_fobj, best_constrains,
            solution, is_converged, quality)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Continuous Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusCusResult(_VitaOptimumPlusUnconstrainedResult):
    """Continuous Unconstrained Method Result (VO+)"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 solution, is_converged, quality):
        _VitaOptimumPlusResult.__init__(self, dim, fobj, best_fobj,
                                        solution, is_converged, quality)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Continuous Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusIcsResult(_VitaOptimumPlusConstrainedResult):
    """Integer Constrained Method Result (VO+)"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 best_constrains, solution, is_converged, quality):
        _VitaOptimumPlusConstrainedResult.__init__(
            self, dim, fobj, best_fobj, best_constrains,
            solution, is_converged, quality)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Integer Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusIusResult(_VitaOptimumPlusUnconstrainedResult):
    """Integer Unconstrained Method Result (VO+)"""

    def __init__(self, dim, low, high, fobj, best_fobj,
                 solution, is_converged, quality):
        _VitaOptimumPlusResult.__init__(self, dim, fobj, best_fobj,
                                        solution, is_converged, quality)
        self._low = low
        self._high = high

    def to_string(self, separator='\n'):
        lines = [
            f"Integer Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusPcsResult(_VitaOptimumPlusConstrainedResult):
    """Permutation Constrained Method Result (VO+)"""

    def to_string(self, separator='\n'):
        lines = [
            f"Permutation Constrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusPusResult(_VitaOptimumPlusUnconstrainedResult):
    """Permutation Unconstrained Method Result (VO+)"""

    def to_string(self, separator='\n'):
        lines = [
            f"Permutation Unconstrained Global Optimization Method Result:",
        ]
        lines.append(super().to_string(separator))
        return separator.join(lines)


class VitaOptimumPlusMusResult(_VitaOptimumPlusUnconstrainedResult):
    def __init__(self, fobj, best_fobj, continuous_solution,
                 integer_solution, binary_solution,
                 permutations_solution, is_converged,
                 quality):
        self._dim = 0
        mixed_solution = [
            continuous_solution,
            integer_solution,
            binary_solution,
            permutations_solution
        ]
        _VitaOptimumPlusUnconstrainedResult.__init__(
            self, self._dim, fobj, best_fobj, mixed_solution,
            is_converged, quality)

    def to_string(self, separator='\n'):
        lines = [
            f"Mixed Unconstrained Global Optimization Method Result:",
            f"Best function: {self._best_fobj}",
            f"Found continuous solution: {self._solution[0]}",
            f"Found integer solution: {self._solution[1]}",
            f"Found binary solution: {self._solution[2]}",
            f"Found permutations solution: {self._solution[3]}",
            f"Is converged: {self._convergence}",
        ]
        lines.append(self._print_quality(separator))
        return separator.join(lines)

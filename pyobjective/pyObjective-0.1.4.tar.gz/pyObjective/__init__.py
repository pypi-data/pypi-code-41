from scipy.optimize import dual_annealing
from prettytable import PrettyTable


class Variable:

    def __init__(self, name, value, bounds, description=None):
        """ Create a variable

        Parameters
        ----------
        name: str
            name for the variable
        value: float
            numerical value of the variable. May be used as initial guess or to check model compilation.
        bounds: (lower float, upper float)
            range of possible values
        description: str, optional
            longer description of variable, for easy referencing in results.

        Returns
        -------
        Variable

        """
        self.name = name
        self.value = value
        self.bounds = bounds
        self.description = description

        self.index = -1
        self.mode = 'float'
        self.vector = []

    def __call__(self, vec=[], mode=None):
        """ Returns an appropriate form of the variable.

        Parameters
        ----------
        vec: 1D array or list
            vector to substitute into variables
        mode:
            type of return on calling the variable.

        Returns
        -------
        object:
            If mode is 'float' or 'value', the variables value is returned (float).
            If mode is 'index', the index of this variable within the vector is returned (int).
            If mode is 'obj', the returned style is such that it can be used by scipy's optimize features (vec[int])

        """
        if mode is None:
            mode = self.mode

        if mode == 'float' or mode == 'value':  # identical behaviour
            return self.value
        elif mode == 'index':
            return self.index
        elif mode == 'obj':
            return self.vector[self.index]
        else:
            raise TypeError(
                'Call on variable doesnt know which mode to use, or mode specified is not allowed. '
                'Allowed modes include (float, value, index, obj). '
                'Check for typos.')



class Model:

    def __init__(self):
        """
        Initializes the model.
        """
        self.N = 0
        self.vars = []
        self.bounds = []
        self.objective = None
        self.solution = None
        self.solution_vector = None

    def add_var(self, var):
        """
        Adds a variable to the model. Also updates indices and variable lists.

        Parameters
        ----------
        var: Variable
            Variable to be added

        """
        var.index = self.N
        self.N += 1
        self.vars.append(var)
        self.bounds.append(var.bounds)

    def solve(self, objective=None, solveOptions={}):
        """
        Solves the model. Uses scipy's dual_annealing method to efficiently find global optimal.
        In the future, I will try to make it generic enough to use a solver of your choice.

        Parameters
        ----------
        objective: method, optional
            Allows user to define the objective function when the solve method is called.
            Replaces internal self.objective method.

        solveOptions: dict, optional
            dictionary of all additional parameters that can be provided to scipy.optimize.dual_annealing()

        Returns
        -------
        OptimizeResult:
            result dictionary as returned by Scipy
            Also stores the solution within the model object (accessible by model.solution and model.solution_vector)

        """
        if objective is not None:
            self.objective = objective

        res = dual_annealing(self.evaluate, self.bounds, **solveOptions)

        for v in self.vars:
            v.mode = 'float'

        self.solution = res
        self.solution_vector = res.x

        return res

    def evaluate(self, vec):
        """
        Evaluates the cost for the model for a given vector.

        Parameters
        ----------
        vec: 1D array or list
            list of floats, vector of variable values

        Returns
        -------
        float:
            cost evaluated for this vector

        """
        for v in self.vars:
            v.mode = 'obj'
            v.vector = vec  # extracts the relevant position from vector, and stores it in its own value

        return self.objective()  # return the cost

    def display_results(self):
        """
        Simple method to display the cost and the variables neatly.
        """
        # evaluate cost
        t = PrettyTable(['Cost: ', self.evaluate(self.solution_vector)])
        print(t)

        # print variables
        t = PrettyTable(['Variable', 'Value', 'Description'])
        for v in self.vars:
            t.add_row([v.name, v(self.solution_vector), v.description])
        print(t)


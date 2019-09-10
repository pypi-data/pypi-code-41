import json
import math
import numpy as np
from scipy import optimize
from dplus.CalculationInput import CalculationInput
from dplus.CalculationRunner import LocalRunner
from dplus.FileReaders import _handle_infinity_for_json, NumpyHandlingEncoder


class GenerateWrapper:
    def __init__(self, calc_input, dplus_runner=None):
        self.input=calc_input
        self.dplus_runner=dplus_runner
        if not self.dplus_runner:
            self.dplus_runner = LocalRunner()

    def run_generate(self, xdata, *params):
        '''
        scipy's optimization algorithms require a function that receives an x array and an array of parameters, and
        returns a y array.
        this function will be called repeatedly, until scipy's optimization has completed.
        '''
        self.input.set_mutable_parameter_values(params) #we take the parameters given by scipy and place them inside our parameter tree
        generate_results=self.dplus_runner.generate(self.input) #call generate
        return np.array(generate_results.y) #return the results of the generate call


class MinimizeFitter:
    '''
    placeholder class. it should be possible to greatly increase list of optimizers we can run if we use scipy's minimize, not just scipy's curve_fit
    '''
    def __init__(self, calc_input):
        self.input = calc_input
        self.generate_runner = GenerateWrapper(calc_input)
        self.kwargs = {}

    def run_generate(self, xdata, *params):
        return self.generate_runner.run_generate(xdata, *params)

    def fnc2min(self, xdata, *params):
        return self.run_generate(xdata, *params) - self.input.y


class CurveFitter:
    '''
    a class for running fitting using scipy's optimize.curve_fit.
    it can be customized with any of the arguments scipy's curve_Fit can take, documented on the scipy website, by adding the
    values for those arguments to self,kwargs (eg, method="lm")

    some of the options allow writing and passing references to your own code.
    specifically:
    jac and loss for non-lm, Dfun for lm
    '''
    def __init__(self, calc_input):
        self.input = calc_input
        self.generate_runner = GenerateWrapper(calc_input)
        self.kwargs = {}

    def run_generate(self, xdata, *params):
        return self.generate_runner.run_generate(xdata, *params)

    def get_args(self, y):
        #a work in progress function that translates as many of the existing fitting parameters as possible into arguments to curve_fit
        #based on:
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.leastsq.html
        #https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html

        fit_prefs=self.input.FittingPreferences
        if fit_prefs.minimizer_type=="Trust Region" and fit_prefs.trust_region_strategy_type=="Levenberg-Marquardt":
            self.kwargs['method']='lm'
            return #levenberg marquardt can't accept most of the remaining arguments

        if fit_prefs.minimizer_type == "Trust Region" and fit_prefs.trust_region_strategy_type == "Dogleg":
            self.kwargs['method']='dogbox' #I think?
        else:
            self.kwargs['method'] = 'trf' #this is what scipy has to offer and hence worth testing, NOT a translation of D+'s other methods

        sigma, bounds=self.input.get_mutable_parameter_options()
        #the sigma given in parameters does not match the sigma scipy expects, which is for points of y
        #bounds is only allowed with methods other than lm
        self.kwargs['bounds']=bounds

        loss_dict={
            "Huber Loss" : "huber",
            "Soft L One Loss": "soft_l1",
            "Cauchy Loss": "cauchy",
            "Arctan Loss": "arctan",
            "Tolerant Loss": NotImplementedError, #ρ(s,a,b)=b * log(1+e^((s−a)/b))− b * log(1+e^ (−a/b)) #a and b are loss func params
            "Trivial Loss": "linear" #scipy's default
        }
        loss = loss_dict[fit_prefs.loss_function]
        self.kwargs['loss']=loss
        self.kwargs['max_nfev'] =fit_prefs.fitting_iterations
        self.kwargs['diff_step'] =fit_prefs.step_size
        self.kwargs['ftol'] = fit_prefs.convergence * np.mean(y) * 1e-3
        self.kwargs['gtol'] = self.kwargs['ftol'] * 1e-4



        pass


    def run_fit(self):
        #all fittings needs x, y, and initial params
        x_data = self.input.x
        y_data = self.input.y
        p0 = self.input.get_mutable_parameter_values()

        #load optional additional parameters
        self.get_args(y_data)


        #call the specific fitting you want
        popt, pcov = optimize.curve_fit(self.run_generate, x_data, y_data, p0=p0, **self.kwargs)

        # popt is the optimized set of parameters from those we have indicated as mutable
        # we can insert them back into our CalculationInput and create the optimized parameter tree
        self.input.set_mutable_parameter_values(popt)

        # we can re-run generate to get the results of generate with them
        self.best_results = self.generate_runner.dplus_runner.generate(self.input)

    def save_dplus_arrays(self, outfile):
        '''
        a function for saving fit results in the bizarre special format D+ expects
        :param outfile:
        :return:
        '''
        param_tree= self.best_results._calc_data._get_dplus_fit_results_json()
        result_dict = {
            "ParameterTree": param_tree,
            "Graph": list(self.best_results.y)
        }
        with open(outfile, 'w') as file:
            json.dump(_handle_infinity_for_json(result_dict), file, cls=NumpyHandlingEncoder)


def main(infile, outfile):
    input = CalculationInput.load_from_state_file(infile)
    fitter = CurveFitter(input)
    fitter.run_fit()
    fitter.save_dplus_arrays(outfile)


# main(r"C:\Users\yael\Sources\dplus\PythonInterface\tests\reviewer_tests\files_for_tests\fit\gpu\short\Cylinder_3EDFit\Cylinder_3EDFit_fixed.state",
main(r"C:\Users\yael\Sources\temp\sphere dogleg.state",
     r"C:\Users\yael\Sources\temp\testfitoutput.json")

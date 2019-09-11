"""Implementation of the main Biogeme class that combines the database and the model specification.

:author: Michel Bierlaire
:date: Tue Mar 26 16:45:15 2019

"""

import numpy as np
import pandas as pd
import pickle
from datetime import datetime
import multiprocessing as mp

import biogeme.database as db
import biogeme.cbiogeme as cb
import biogeme.expressions as eb
import biogeme.tools as tools
import biogeme.version as bv
import biogeme.results as res
import biogeme.exceptions as excep
import biogeme.filenames as bf
import biogeme.messaging as msg
import biogeme.optimization as opt

#import yep

class BIOGEME:
    """Main class that combines the database and the model specification.

    It works in two modes: estimation and simulation.

    """

    def __init__(self,
                 database,
                 formulas,
                 numberOfThreads=None,
                 numberOfDraws=1000,
                 seed=None,
                 skipAudit=False,
                 removeUnusedVariables=True,
                 missingData=99999):
        """Constructor

        :param database: choice data.
        :type database: biogeme.database

        :param formulas: expression or dictionary of expressions that
             define the model specification.  The concept is that each
             expression is applied to each entry of the database. The
             keys of the dictionary allow to provide a name to each
             formula.  In the estimation mode, two formulas are
             needed, with the keys 'loglike' and 'weight'. If only one
             formula is provided, it is associated with the label
             'loglike'. If no formula is labeled 'weight', the weight
             of each piece of data is supposed to be 1.0. In the
             simulation mode, the labels of each formula are used as
             labels of the resulting database.
        :type formulas: biogeme.expressions.Expression, or dict(biogeme.expressions.Expression)

        :param numberOfThreads: multi-threading can be used for
            estimation. This parameter defines the number of threads
            to be used. If the parameter is set to None, the number of
            available threads is calculated using
            cpu_count(). Ignored in simulation mode. Defaults: None.
        :type numberOfThreads:  int

        :param numberOfDraws: number of draws used for Monte-Carlo
            integration. Default: 1000.
        :type numberOfDraws: int

        :param seed: seed used for the pseudo-random number
            generation. It is useful only when each run should
            generate the exact same result. If None, a new seed is
            used at each run. Default: None.
        :type seed: int

        :param skipAudit: if True, does not check the validity of the
            formulas. It may save significant amount of time for large
            models and large data sets. Default: False.
        :type skipAudit: bool

        :param removeUnusedVariables: if True, all variables not used
           in the expression are removed from the database. Default:
           True.
        :type removeUnusedVariables: bool

        :param missingData: if one variable has this value, it is
           assumed that a data is missing and an exception will be
           triggered. Default: 99999.
        :type missingData: float

        """

        ## Logger that controls the output of messages to the screen and log file.
        self.logger = msg.bioMessage()
        self.logger.debug("Initialize Biogeme...")
        if not skipAudit:
            database.data = database.data.replace({True:1, False:0})
            self.logger.debug("    Audit database...")
            listOfErrors, listOfWarnings = database._audit()
            if listOfWarnings:
                self.logger.warning('\n'.join(listOfWarnings))
            if listOfErrors:
                self.logger.warning('\n'.join(listOfErrors))
                raise excep.biogemeError("\n".join(listOfErrors))

        ## Keyword used for the name of the loglikelihood formula. Default: 'loglike'
        self.loglikeName = 'loglike'
        ## Keyword used for the name of the weight formula. Default: 'weight'
        self.weightName = 'weight'
        ## Name of the model. Default: 'biogemeModelDefaultName'
        self.modelName = 'biogemeModelDefaultName'
        ## monteCarlo is True if one of the expression involves a
        # Monte-Carlo integration.
        self.monteCarlo = False
        np.random.seed(seed)

        self.logger.debug("    Retrieve formulas...")

        if not isinstance(formulas,dict):

            ## Object of type biogeme.expressions.Expression
            ## calculating the formula for the loglikelihood
            self.loglike = formulas

            ## Object of type biogeme.expressions.Expression
            ## calculating the weight of each observation in the
            ## sample
            self.weight = None

            ## Dictionary containing Biogeme formulas of type
            ## biogeme.expressions.Expression.
            # The keys are the names of the formulas.
            self.formulas = dict({self.loglikeName:formulas})
        else:
            self.loglike = formulas.get(self.loglikeName)
            self.weight = formulas.get(self.weightName)
            self.formulas = formulas

        ## biogeme.database object
        self.database = database

        ## Init value of the likelihood function
        self.initLogLike = None

        if removeUnusedVariables:
            usedVariables = set()
            for k, f in self.formulas.items():
                usedVariables = usedVariables.union(f.setOfVariables())
            if self.database.isPanel():
                usedVariables.add(self.database.panelColumn)
            unusedVariables = set(self.database.data.columns) - usedVariables
            self.logger.general(f"Remove {len(unusedVariables)} unused variables from the database as only {len(usedVariables)} are used.")
            self.database.data = self.database.data.drop(columns=list(unusedVariables))

        if not skipAudit:
            self.logger.debug("   Audit formulas...")
            self._audit()
        self.logger.debug("   Create C++ object...")
        if self.database.isPanel():
            self.database._buildPanelMap()
            ## Object containing the C++ implementation used by Biogeme.
            self.theC = cb.pyBiogeme()
            self.theC.setPanel(True)
            self.theC.setDataMap(self.database.individualMap)
        else:
            self.theC = cb.pyBiogeme()
        self.logger.debug("   Transmit data...")
        self.theC.setData(self.database.data)
        self.theC.setMissingData(missingData)
        self.logger.debug("   Prepare literals...")
        self._prepareLiterals()
        ## Boolean variable, True if the HTML file with the results must be generated.
        self.generateHtml = True
        ## Boolean variable, True if the pickle file with the results must be generated.
        self.generatePickle = True


        ## Number of threads used for parallel computing. Default: the number of CPU available.
        self.numberOfThreads = mp.cpu_count() if numberOfThreads is None else numberOfThreads
        start_time = datetime.now()
        self.logger.debug("   Generate draws...")
        self._generateDraws(numberOfDraws)
        if self.monteCarlo:
            self.theC.setDraws(self.database.theDraws)
        ## Time needed to generate the draws.
        self.drawsProcessingTime = datetime.now() - start_time
        self.logger.debug("   Get signatures...")
        if self.loglike is not None:
            self.logger.debug("   Get signatures for loglikelihood...")

            ## Internal signature of the formula for the loglikelihood
            self.loglikeSignatures = self.loglike.getSignature()
            if self.weight is None:
                self.logger.debug("   set expressions...")
                self.theC.setExpressions(self.loglikeSignatures,
                                         self.numberOfThreads)
            else:
                ## Internal signature of the formula for the weight
                self.weightSignatures = self.weight.getSignature()
                self.theC.setExpressions(self.loglikeSignatures,
                                         self.numberOfThreads,
                                         self.weightSignatures)
        self.logger.debug("   Done...")


    def _audit(self):
        """Each expression provides an audit function, that verifies its
           validity. Each formula is audited, and the list of errors
           and warnings reported.

           :raise biogemeError: if the formula has issues, an error is
                                detected and an exception is raised.

        """

        listOfErrors = []
        listOfWarnings = []
        for k, v in self.formulas.items():
            err, war = v.audit(self.database)
            listOfErrors += err
            listOfWarnings += war
        if listOfWarnings:
            self.logger.warning('\n'.join(listOfWarnings))
        if listOfErrors:
            self.logger.warning('\n'.join(listOfErrors))
            raise excep.biogemeError("\n".join(listOfErrors))

    def _generateDraws(self, numberOfDraws):
        """If Monte-Carlo integration is involved in one of the formulas, this
           function instructs the database to generate the draws.

        Args:
            numberOfDraws: self explanatory (int)
        """


        ## Number of draws for Monte-Carlo integration.
        self.numberOfDraws = numberOfDraws
#        drawTypes = {}
#        for k,v in self.formulas.items() :
#            d = v.getDraws()
#            if d:
#                drawTypes = dict(drawTypes,**d)
        ## Draws
        self.monteCarlo = len(self.allDraws) > 0
        if self.monteCarlo:
            self.database.generateDraws(self.allDraws,
                                        self.drawNames,
                                        numberOfDraws)

    def getBoundsOnBeta(self, betaName):
        """ Returns the bounds on the parameter as defined by the user.

        :param betaName: name of the parameter
        :type betaName: string
        :return: lower bound, upper bound
        :rtype: tuple
        :raises biogemeError: if the name of the parameter is not found.
        """

        if betaName not in self.freeBetaNames:
            raise excep.biogemeError(f"Unknown parameter {betaName}")
        index = self.freeBetaNames.index(betaName)
        return self.bounds[index]

    def _prepareLiterals(self):
        """ Extract from the formulas the literals (parameters,
        variables, random variables) and decide a numbering convention.
        """

        collectionOfFormulas = [f for k, f in self.formulas.items()]
        variableNames = list(self.database.data.columns.values)

        self.elementaryExpressionIndex, \
        self.allFreeBetas, \
        self.freeBetaNames, \
        self.allFixedBetas, \
        self.fixedBetaNames, \
        self.allRandomVariables, \
        self.randomVariableNames, \
        self.allDraws, \
        self.drawNames = \
            eb.defineNumberingOfElementaryExpressions(collectionOfFormulas,
                                                      variableNames)

        ### List of tuples (ell,u) containing the lower and upper bounds
        # for each free parameter
        self.bounds = list()
        for x in self.freeBetaNames:
            self.bounds.append((self.allFreeBetas[x].lb,
                                self.allFreeBetas[x].ub))
        ## List of ids of the free beta parameters (those to be estimated)
        self.betaIds = [i for i in range(len(self.freeBetaNames))]

        ## List of initial values of the free beta parameters (those to be estimated)
        self.betaInitValues = [float(self.allFreeBetas[x].initValue) for x in self.freeBetaNames]
        ## Values of the fixed parameters (not estimated).
        self.fixedBetaValues = [float(self.allFixedBetas[x].initValue) for x in self.fixedBetaNames]

    def calculateInitLikelihood(self):
        """Calculate the value of the log likelihood function

        The default values of the parameters are used.

        :return: value of the log likelihood.
        :rtype: float.
        """

        ## Value of the loglikelihood for the default values of the parameters.
        self.initLogLike = self.calculateLikelihood(self.betaInitValues)
        return self.initLogLike

    def calculateLikelihood(self, x):
        """ Calculates the value of the log likelihood function

        :param x: vector of values for the parameters.
        :type x: list(float)

        :return: the calculated value of the log likelihood
        :rtype: float.

        :raises ValueError: if the length of the list x is incorrect.

        """

        if len(x) != len(self.betaInitValues):
            raise ValueError("Input vector must be of length {} and not {}".format(len(self.betaInitValues), len(x)))

        f = self.theC.calculateLikelihood(x, self.fixedBetaValues)

        self.logger.general(f"Log likelihood: {f:10.7g}")
        return f

    def calculateLikelihoodAndDerivatives(self, x, hessian=False, bhhh=False):
        """Calculate the value of the log likelihood function and its derivatives.

        :param x: vector of values for the parameters.
        :type x: list(float)
        :param hessian: if True, the hessian is calculated. Default: False.
        :type hessian: bool
        :param bhhh: if True, the BHHH matrix is calculated. Default: False.
        :type bhhh: bool

        :return: f, g, h, bh where

                - f is the value of the function (float)
                - g is the gradient (numpy.array)
                - h is the hessian (numpy.array)
                - bh is the BHHH matrix (numpy.array)

        :rtype: tuple  float, numpy.array, numpy.array, numpy.array

        :raises ValueError: if the length of the list x is incorrect

        """

        if len(x) != len(self.betaInitValues):
            raise ValueError("Input vector must be of length {} and not {}".format(len(betaInitValues), len(x)))
        f, g, h, bh = self.theC.calculateLikelihoodAndDerivatives(x,
                                                                  self.fixedBetaValues,
                                                                  self.betaIds,
                                                                  hessian,
                                                                  bhhh)

        self.logger.general(f"Log likelihood: {f:10.7g} Gradient norm: {np.linalg.norm(g):10.1g}")
        return f, np.asarray(g), np.asarray(h), np.asarray(bh)

    def likelihoodFiniteDifferenceHessian(self, x):
        """Calculate the hessian of the log likelihood function using finite differences.

        May be useful when the analytical hessian has numerical issues.

        :param x: vector of values for the parameters.
        :type x: list(float)

        :return: finite differences approximation of the hessian.
        :rtype: numpy.array

        :raises ValueError: if the length of the list x is incorrect

        """

        def theFunction(x):
            f, g, h, b = self.calculateLikelihoodAndDerivatives(x,
                                                                hessian=False,
                                                                bhhh=False)
            return f, np.asarray(g)
        return tools.findiff_H(theFunction, np.asarray(x))

    def checkDerivatives(self, verbose=False):
        """Verifies the implementation of the derivatives.

        It compares the analytical version with the finite differences approximation.

        :param verbose: if True, the comparisons are reported. Default: False.
        :type verbose: bool

        :rtype: tuple.

        :return: f, g, h, gdiff, hdiff where

            - f is the value of the function,
            - g is the analytical gradient,
            - h is the analytical hessian,
            - gdiff is the difference between the analytical and the
              finite differences gradient,
            - hdiff is the difference between the analytical and the
              finite differences hessian,

        """
        def theFunction(x):
            """ Wrapper function to use tools.checkDerivatives """
            f, g, h, b = self.calculateLikelihoodAndDerivatives(x,
                                                                hessian=True,
                                                                bhhh=False)
            return f, np.asarray(g), np.asarray(h)

        return tools.checkDerivatives(theFunction,
                                      np.asarray(self.betaInitValues),
                                      self.freeBetaNames,
                                      verbose)



    def estimate(self,
                 bootstrap=0,
                 algorithm=opt.scipy,
                 algoParameters=None,
                 cfsqpDefaultBounds=1000.0):
        """Estimate the parameters of the model.

        :param bootstrap: number of bootstrap resampling used to
               calculate the variance-covariance matrix using
               bootstrapping. If the number is 0, bootstrapping is not
               applied. Default: 0.
        :type bootstrap: int

        :param algorithm: optimization algorithm to use for the
               maximum likelihood estimation. If None, cfsqp is
               used. Default: the optimization algorithm available
               with scipy.
        :type algorithm: function

        :param algoParameters: parameters to transfer to the optimization algorithm
        :type algoParameters: dict

        :param cfsqpDefaultBounds: if the user does not provide bounds
              on the parameters, CFSQP assumes that the bounds are
              [-cfsqpDefaultBounds,cfsqpDefaultBounds]
        :type cfsqpDefaultBounds: float

        :return: object containing the estimation results.
        :rtype: biogeme.bioResults

        Example::

            # Create an instance of biogeme
            biogeme  = bio.BIOGEME(database, logprob)
            # Gives a name to the model
            biogeme.modelName = "mymodel"
            # Estimate the parameters
            results = biogeme.estimate()

        :raises biogemeError: if no expression has been provided for the likelihood

        """

        if self.loglike is None:
            raise excep.biogemeError("No log likelihood function has been specificed")
        if len(self.freeBetaNames) == 0:
            raise excep.biogemeError(f"There is no parameter to estimate in the formula: {self.loglike}.")


        self.algorithm = algorithm
        self.algoParameters = algoParameters
        self.cfsqpDefaultBounds = cfsqpDefaultBounds

        self.calculateInitLikelihood()


        start_time = datetime.now()
        #        yep.start('profile.out')

        #        yep.stop()

        xstar, nIter, nFunctions, diag = self.optimize(self.betaInitValues)
        ## Runnig time of the optimization algorithm
        self.optimizationTime = datetime.now() - start_time
        ## Information provided by the optimization algorithm after completion.
        self.optimizationMessage = diag
        ## Number of times that the loglikelihood function has been evaluated.
        self.numberOfFunctionEval = nFunctions
        ## Number of iterations performed by the optimization algorithm.
        self.numberOfIterations = nIter
        fgHb = self.calculateLikelihoodAndDerivatives(xstar,
                                                      hessian=True,
                                                      bhhh=True)
        if not np.isfinite(fgHb[2]).all():
            self.logger.warning("Numerical problems in calculating the analytical hessian. Finite differences is tried instead.")
            finDiffHessian = self.likelihoodFiniteDifferenceHessian(xstar)
            if not np.isfinite(fgHb[2]).all():
                self.logger.warning("Numerical problems with finite difference hessian as well.")
            else:
                fgHb = fgHb[0], fgHb[1], finDiffHessian, fgHb[3]
        ## numpy array, of size B x K,
        # where
        #        - B is the number of bootstrap iterations
        #        - K is the number pf parameters to estimate
        self.bootstrapResults = None
        if bootstrap > 0:
            start_time = datetime.now()

            self.logger.general("Re-estimate the model {} times for bootstrapping".format(bootstrap))
            self.bootstrapResults = np.empty(shape=[bootstrap, len(xstar)])
            for b in range(bootstrap):
                if self.database.isPanel():
                    sample = self.database.sampleIndividualMapWithReplacement()
                    self.theC.setDataMap(sample)
                else:
                    sample = self.database.sampleWithReplacement()
                    self.theC.setData(sample)
                x_br, nIter_br, nFunctions_br, diag_br = self.optimize(xstar)
                self.bootstrapResults[b] = x_br
#            print("*")

            ## Time needed to generate the bootstrap results
            self.bootstrapTime = datetime.now() - start_time

        rawResults = res.rawResults(self,
                                    xstar,
                                    fgHb,
                                    bootstrap=self.bootstrapResults)
        r = res.bioResults(rawResults)
        if self.generateHtml:
            r.writeHtml()
        if self.generatePickle:
            r.writePickle()
        return r

    def optimize(self, startingValues):
        """ Calls the optimization algorithm.

        The function self.algorithm is called. If None, CFSQP is invoked.

        :param startingValues: initial values of the parameters.
        :type startingValues: list of floats

        :returns: x, nit, nfev, message, where

               - x is the solution found,
               - nit is the number of iterations performed,
               - nfev is the number of time that the objective function has been evaluated, and
               - message is the diagnostic provided by the algorithm.

        :rtype: tuple
        """

        if self.algorithm is None:
            parameters = {'mode':100,
                        'iprint':self.logger.screenLevel,
                        'miter':1000,
                        'eps':6.05545e-06}
            return self.cfsqp(self.betaInitValues,
                              self.fixedBetaValues,
                              self.betaIds,
                              self.bounds,
                              parameters)
        else:
            return self.algorithm(self.calculateLikelihoodAndDerivatives,
                                  self.betaInitValues,
                                  self.fixedBetaValues,
                                  self.betaIds,
                                  self.bounds,
                                  self.algoParameters)


    def simulate(self, theBetaValues=None):
        """Applies the formulas to each row of the database.

        :param theBetaValues: values of the parameters to be used in
                the calculations. If None, the default values are
                used. Default: None.
        :type theBetaValues: dict(str, float) or list(float)

        :return: a pandas data frame with the simulated value. Each
              row corresponds to a row in the database, and each
              column to a formula.

        :rtype: Pandas data frame

        Example::

              # Read the estimation results from a file
              results = res.bioResults(pickleFile='myModel.pickle')
              # Simulate the formulas using the nominal values
              simulatedValues = biogeme.simulate(betaValues)

        :raises biogemeError: if the number of parameters is incorrect

        """

        if theBetaValues is None:
            betaValues = self.betaInitValues
        else:
            if type(theBetaValues) is not dict:
                if len(theBetaValues) != len(self.betaInitValues):
                    err = f"The value of {len(self.betaInitValues)} parameters should be provided, not {len(theBetaValues)}."
                    raise excep.biogemeError(err)

                betaValues = theBetaValues
            else:
                betaValues = list()
                for i in range(len(self.freeBetaNames)):
                    x = self.freeBetaNames[i]
                    if x in theBetaValues:
                        betaValues.append(theBetaValues[x])
                    else:
                        betaValues.append(self.betaInitValues[i])

        output = pd.DataFrame(index=self.database.data.index)
        for k, v in self.formulas.items():
            signature = v.getSignature()
            result = self.theC.simulateFormula(signature,
                                               betaValues,
                                               self.fixedBetaValues,
                                               self.database.data)
            output[k] = result
        return output


    def confidenceIntervals(self, betaValues, intervalSize=0.9):
        """Calculate confidence intervals on the simulated quantities


        :param betaValues: array of parameters values to be used in
               the calculations. Typically, it is a sample drawn from
               a distribution.
        :type betaValues: list(dict(float))

        :param intervalSize: size of the reported confidence interval,
                    in percentage. If it is denoted by s, the interval
                    is calculated for the quantiles (1-s)/2 and
                    (1+s)/2. The default (0.9) corresponds to
                    quantiles for the confidence interval [0.05,0.95].
        :type intervalSize: float

        :return: two pandas data frames 'left' and 'right' with the
            same dimensions. Each row corresponds to a row in the
            database, and each column to a formula. 'left' contains the
            left value of the confidence interval, and 'right' the right
            value

            Example::

                # Read the estimation results from a file
                results = res.bioResults(pickleFile='myModel.pickle')
                # Retrieve the names of the betas parameters that have been estimated
                betas = biogeme.freeBetaNames
                # Draw 100 realization of the distribution of the estimators
                b = results.getBetasForSensitivityAnalysis(betas, size=100)
                # Simulate the formulas using the nominal values
                simulatedValues = biogeme.simulate(betaValues)
                # Calculate the confidence intervals for each formula
                left, right = biogeme.confidenceIntervals(b, 0.9)

        :rtype: tuple of two Pandas dataframes.

        """
        listOfResults = []
        for b in betaValues:
            r = self.simulate(b)
            listOfResults += [r]
        allResults = pd.concat(listOfResults)
        r = (1.0-intervalSize)/2.0
        left = allResults.groupby(level=0).quantile(r)
        right = allResults.groupby(level=0).quantile(1.0-r)
        return left, right

    def createLogFile(self, level=3):
        """ Creates a log file with the messages produced by Biogeme.

        The name of the file is the name of the model with an extension .log

        :param level: types of messages to be captured

            - 0: no output
            - 1: warnings
            - 2: only general information
            - 3: more verbose
            - 4: debug messages

            Default: 3.

        :type level: int

        """
        self.logger.createLog(fileLevel=level, fileName=self.modelName)

    def __str__(self):
        r = f'{self.modelName}: database [{self.database.name}]'
        r += str(self.formulas)
        print(r)
        return r

    def cfsqp(self, betas, fixedBetas, betaIds, bounds, parameters):
        """
        Invokes the CFSQP algorithm for estimation

        :param betas: initial values of the parameters to be estimated.
        :type betas: list of float
        :param fixedBetas: values of the parameters that are not estimated.
        :type fixedBetas: list of float
        :param betaIds: list of IDs of the beta to be estimated.
        :type betaIds: list of int
        :param bounds: lower and upper bounds on each parameter.
        :type bounds: list of tuple
        :param parameters: user defined parameters for CFSQP

           - mode=CBA: specifies job options as described below

                 * A = 0: ordinary minimax problems
                 * A = 1: ordinary minimax problems with each individual function replaced by its absolute value, ie, an L_infty problem
                 * B = 0: monotone decrease of objective function after each iteration
                 * B = 1: monotone decrease of objective function after at most four iterations
                 * C = 1: default operation.
                 * C= 2: requires that constraints always be evaluated before objectives during the line search.

           -  iprint: print level indicator with the following options

               * iprint=0: no normal output, only error information (this option is imposed during phase 1)
               * iprint=1: a final printout at a local solution
               * iprint=2: a brief printout at the end of each iteration
               * iprint=3: detailed infomation is printed out at the end of each iteration (for debugging purposes)

           -  miter: maximum number of iterations allowed by the user to solve              the problem


        :type parameters: dict

        """
        lb, ub = zip(*bounds)
        lb = [-self.cfsqpDefaultBounds if v is None else v for v in lb]
        ub = [self.cfsqpDefaultBounds if v is None else v for v in ub]
        self.theC.setBounds(lb, ub)
        mode = parameters.get('mode', 100)
        iprint = parameters.get('iprint', 2)
        if iprint > 3:
            iprint = 3
        miter = parameters.get('miter', 1000)
        eps = parameters.get('eps', 6.05545e-06)

        output = self.theC.cfsqp(betas,
                                 fixedBetas,
                                 betaIds,
                                 mode,
                                 iprint,
                                 miter,
                                 eps)
        return output

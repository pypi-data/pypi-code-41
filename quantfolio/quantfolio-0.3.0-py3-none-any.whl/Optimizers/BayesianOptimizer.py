import numpy as np
from bayes_opt import BayesianOptimization
from . import OptimisationResults

# Bayesian Optimizer for slow backtests
def bayesianOptimizer(portfolio, interval=None, **kwargs):
    # Options
    initPoints = kwargs.get("initPoints", 1)
    noSimulations = kwargs.get("sims", 20) - initPoints

    optResults = OptimisationResults(portfolio.assetNames, rf=portfolio.rf)

    def black_box_function(**kwargs):
        weights = [v for v in kwargs.values()]
        if np.sum(weights) == 0:
            return 0
        normalisedWeights = np.array(weights) / np.sum(weights)
        normalisedWeightsDict = dict(zip(portfolio.assetNames, normalisedWeights))
        results, _ = portfolio.backtest(weights=normalisedWeights, interval=interval)
        optResults.addData(
            {
                **normalisedWeightsDict,
                "Sharpe": results["sharpe"],
                "Returns": results["averageReturns"],
                "Std": results["standardDeviation"],
            }
        )
        return results["sharpe"]

    pbounds = {i: (0, 1) for i in portfolio.assetNames}
    optimizer = BayesianOptimization(
        f=black_box_function, pbounds=pbounds, random_state=1, verbose=False
    )
    optimizer.maximize(init_points=initPoints, n_iter=noSimulations)
    return optResults

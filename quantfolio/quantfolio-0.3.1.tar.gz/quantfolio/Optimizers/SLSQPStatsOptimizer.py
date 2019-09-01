import math
import numpy as np
import scipy.optimize as sco
from . import OptimisationResults

# Sequential Least Squares Programming optimizer using the statistical model for the assets
def slsqpStatsOptimizer(portfolio, interval=None, **kwargs):
    optResults = OptimisationResults(portfolio.assetNames, rf=portfolio.rf)

    def black_box_function(weights):
        results = dict(zip(portfolio.assetNames, weights))
        performance = portfolio.portfolioPerformance(weights)

        results["Sharpe"] = performance["sharpe"]
        results["Std"] = performance["std"]
        results["Returns"] = performance["returns"]
        optResults.addData(results)
        return -performance["sharpe"]

    numberOfAssets = len(portfolio.assetNames)
    constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
    bounds = tuple((0, 1) for x in range(numberOfAssets))
    initial = np.array(numberOfAssets * [1.0 / numberOfAssets])
    sco.minimize(
        black_box_function,
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )
    return optResults

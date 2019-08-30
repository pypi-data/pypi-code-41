import math
from . import OptimisationResults
from .utils import randomWeight, expectedPortfolioRet, expectedPortfolioVar

# Monte Carlo Optimizer using statistical model of the returns distribution
def monteCarloStatsOptimizer(portfolio, interval=None, **kwargs):
    # Options
    noSimulations = kwargs.get("sims", 1000)

    # portfolio.generateReturnsDataframe()
    optResults = OptimisationResults(portfolio.assetNames, rf=portfolio.rf)

    for _ in range(noSimulations):
        randWeights = randomWeight(len(portfolio.assetNames))
        results = dict(zip(portfolio.assetNames, randWeights))

        ret = expectedPortfolioRet(portfolio.assetReturnsDf, randWeights)
        var = expectedPortfolioVar(portfolio.assetReturnsDf, randWeights)
        std = math.sqrt(var)
        sharpe = (ret - portfolio.rf) / std

        results["Sharpe"] = sharpe
        results["Std"] = std
        results["Returns"] = ret

        optResults.addData(results)

    return optResults

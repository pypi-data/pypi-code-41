import math
from . import OptimisationResults
from .utils import randomWeight

# Monte Carlo Optimiser generates random weight of the assets and run full backtest on the weights
def monteCarloOptimizer(portfolio, interval=None, **kwargs):
    # Options
    noSimulations = kwargs.get("sims", 50)

    optResults = OptimisationResults(portfolio.assetNames, rf=portfolio.rf)

    for _ in range(noSimulations):
        randWeights = randomWeight(len(portfolio.assetNames))
        results = dict(zip(portfolio.assetNames, randWeights))
        (backtestRes, _) = portfolio.backtest(weights=randWeights, interval=interval)

        results["Sharpe"] = backtestRes["sharpe"]
        results["Std"] = backtestRes["standardDeviation"]
        results["Returns"] = backtestRes["averageReturns"]

        optResults.addData(results)

    return optResults

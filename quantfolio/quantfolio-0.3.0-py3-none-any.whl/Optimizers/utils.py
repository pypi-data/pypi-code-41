import numpy as np


def expectedPortfolioRet(returns, weight):
    return np.sum(returns.mean() * weight) * 252


def expectedPortfolioVar(returns, weight):
    return np.dot(weight, np.dot(returns.cov() * 252, weight))


def expectedSharpeRatio(returns, weight, rf=0):
    return (expectedPortfolioRet(returns, weight) - rf) / expectedPortfolioVar(
        returns, weight
    )


def sharpe(returns, std, rf=0):
    return (returns - rf) / std


def randomWeight(length):
    w = np.random.random(length)
    w /= np.sum(w)
    return w

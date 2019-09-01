import math
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class OptimisationResults:
    def __init__(self, names, **kwargs):
        self.rf = kwargs.get("rf", 0)
        self.results = pd.DataFrame(columns=["Sharpe", "Returns", "Std"] + names)

    def addData(self, data):
        logging.info(data)
        self.results = self.results.append(data, ignore_index=True)

    def plotEfficientFrontier(self):
        # Show all points
        plt.scatter(
            self.results["Std"],
            self.results["Returns"],
            c=self.results.index,
            marker="o",
        )
        plt.grid(True)
        plt.xlabel("Expected Standard Deviation")
        plt.ylabel("Expected Returns")
        plt.colorbar(label="Index")

        # Show risk-free rate
        plt.axhline(self.rf, label="rf", color="r", linestyle="--")

        # Show Tangent portfolio to point of highest sharpe
        highestSharpe = self.optimisedWeights()
        x = np.linspace(0, self.results["Std"].max())
        y = highestSharpe["Sharpe"] * x + self.rf
        plt.plot(
            x,
            y,
            label=f'y = {highestSharpe["Sharpe"]:.4f}x + {self.rf}',
            color="r",
            linestyle="--",
        )

        plt.legend()
        plt.show()

    def plotConvergence(self):
        # Show maximum sharpe at each iteration
        plt.subplot(221)
        plt.plot(self.results.cummax()["Sharpe"])
        plt.title("Max Sharpe")

        # Show difference between sharpe
        plt.subplot(222)
        plt.plot(self.results.diff().abs()["Sharpe"])
        plt.title("Difference Between Sharpe")

        # Select subset of top 10% of portfolio
        numOfAssets = self.results.shape[1] - 3
        numOfTopAllocations = max(10, math.ceil(0.05 * self.results.shape[0]))
        topAllocations = self.results.sort_values(by=["Sharpe"]).iloc[
            -numOfTopAllocations:, 3:
        ]

        # Show distribution of asset allocation for each asset for stability test
        plt.subplot(212)
        violinData = list(
            map(lambda x: topAllocations[x].values, topAllocations.columns)
        )
        plt.violinplot(violinData, showmeans=True)
        plt.xticks(range(1, 1 + numOfAssets), labels=topAllocations.columns)
        plt.title("Allocation for each asset for top portfolios")
        plt.show()

    def optimisedWeights(self):
        return self.results.iloc[self.results["Sharpe"].idxmax()]


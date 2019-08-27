import numpy as np

from math import log2
from pandas import read_csv
from sklearn.metrics import silhouette_score


class Observer:
    """Observe and extract information about a dataset.

    Arguments
        __filepath: string
            The dataset's absolute/relative path. Must be a CSV format file.

        __target_i: {-1, 0}
            The target's column index. The default is -1.

    Return
        An Observer object
    """
    def __init__(self, filepath, target_i=-1, header=None, index_col=None):
        self.__filepath = filepath
        self.__target_i = target_i

        self.__header = header
        self.__index_col = index_col

        self.__filedata = None

    def __sep(self):
        with open(self.__filepath, 'r') as file:
            line = file.readline()

        comma = line.count(',')
        semicolon = line.count(';')

        return ',' if comma > semicolon else ';'

    def __data(self, na_values=[]):
        if self.__filedata:
            return self.__filedata

        na_values = ['?'] + na_values

        data = read_csv(self.__filepath,
                        self.__sep(),
                        header=self.__header,
                        index_col=self.__index_col,
                        na_values=na_values)

        _, n_columns = data.shape

        # Initial and final column index (exclusive on stop)
        i = self.__target_i + 1            # initial
        j = n_columns + self.__target_i    # final + 1 (because it's exclusive)

        x = data.iloc[:, i:j]
        y = data.iloc[:, self.__target_i]

        return x, y

    def __x(self, na_values=[]):
        x, y = self.__data(na_values)
        return x

    def __y(self, na_values=[]):
        x, y = self.__data(na_values)
        return y

    def __column(self, j):
        j = self.__target_i if j is None else j
        column = self.__y() if j == self.__target_i else self.__x().iloc[:, j]
        return column

    def n_instances(self):
        """Get the number of instances."""
        x = self.__x()
        m, _ = x.shape
        return m

    def n_features(self):
        """Get the number of features."""
        x = self.__x()
        _, n = x.shape
        return n

    def n_targets(self):
        """Get the number of targets."""
        y = self.__y()
        targets = set(y.values)
        return len(targets)

    def silhouette(self):
        """Get the mean Silhouette Coefficient for all samples."""
        x = self.__x()
        y = self.__y()

        return silhouette_score(x, y)

    def entropy(self, j=None):
        """Get the samples' entropy.

        :param j: int (default target_i)
            Column index.

        :return: float
        """
        column = self.__column(j).values

        sety, counts = np.unique(column, return_counts=True)
        total = sum(counts)

        result = 0
        for n in counts:
            p = n / total
            result = result - p * log2(p)

        return result

    def imbalanced(self, j=None):
        """Get the unbalaced metric, where 1 is very balanced and 0 extremely unbalaced.

        :param j: int (default target_i)
            Column index.

        :return: float
        """
        column = set(self.__column(j).values)
        n = len(column)

        return self.entropy(j) / log2(n)

    def n_binary_features(self):
        """Get the number of binary features, i.e., features with only 2 labels."""
        x = self.__x()
        m, n = x.shape

        bin_features = [len(set(x.iloc[:, j])) == 2 for j in range(n)]

        return sum(bin_features)

    def majority_class_size(self):
        """Get the number of instances labeled with the most frequent class."""
        y = self.__y()
        sety, counts = np.unique(y, return_counts=True)

        return np.max(counts)

    def minority_class_size(self):
        """Get the number of instances labeled with the least frequent class."""
        y = self.__y()
        sety, counts = np.unique(y, return_counts=True)

        return np.min(counts)

    def features_with_na(self, na_values=[]):
        """Get the number of features with missing values.

        Arguments:
            na_values: list (default [])
                a list of strings or ints to interpret as NaN values.
        """
        x = self.__x(na_values)
        x_na = x.isnull().any()

        return x_na.sum()

    def missing_values(self, na_values=[]):
        """Get the number of missing values.

        Arguments:
            na_values: list (default [])
                a list of strings or ints to interpret as NaN values.
        """
        x = self.__x(na_values)
        y = self.__y(na_values)

        x_na = x.isnull()
        y_na = y.isnull()

        x_na_sum = x_na.sum().sum()
        y_na_sum = y_na.sum().sum()

        return x_na_sum + y_na_sum

    def extract(self):
        """Extract all the observed information.

        Return
            [n_instances,
             n_features,
             n_targets,
             silhouette,
             imbalanced,
             n_binary_features,
             majority_class_size,
             minority_class_size,
             features_with_na,
             missing_values]
        """
        ins = self.n_instances()
        fea = self.n_features()
        tar = self.n_targets()
        sil = self.silhouette()
        unb = self.imbalanced()
        nbi = self.n_binary_features()
        maj = self.majority_class_size()
        mio = self.minority_class_size()
        fna = self.features_with_na()
        nav = self.missing_values()

        return [ins, fea, tar, sil, unb, nbi, maj, mio, fna, nav]


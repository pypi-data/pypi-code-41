# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

"""
See:
    Ricardo Baeza-Yates and Berthier Ribeiro-Neto. 2011.
    Modern Information Retrieval: The Concepts and Technology Behind Search.
    Addison-Wesley Publishing Company, USA.
    -- https://dl.acm.org/citation.cfm?id=1796408
"""
from typing import TypeVar

import numpy as np

from crecs import ds
from crecs.ds.abc import DType

T = TypeVar("T")

# precision(y_true, y_pred, at=10)
def is_in(self: ds.Dense[DType], other: ds.Dense[DType]) -> ds.Dense[bool]:
    a = self._data
    b = other._data
    n = len(a)
    out = np.zeros_like(a, bool)

    for i in range(n):
        out[i] = np.isin(a[i], b[i], assume_unique=True)

    return ds.DenseMatrix(out)


def precision(
    relevant: ds.IDense, ranking: ds.IDense, *, at: int = 0
) -> ds.Array[np.float32]:
    at = at or ranking.shape[1]

    return ds.Array(is_in(ranking[:, :at], relevant)._data.sum(1) / at)


def recall(
    relevant: ds.IDense, ranking: ds.IDense, *, at: int = 0
) -> ds.Array[np.float32]:
    at = at or ranking.shape[1]

    return ds.Array(
        is_in(ranking[:, :at], relevant)._data.sum(1) / relevant.shape[1]
    )


def average_precision(
    relevant: ds.IDense, ranking: ds.IDense, *, at: int = 0
) -> ds.Array[np.float32]:

    hits = is_in(ranking, relevant)._data
    prec = hits * np.cumsum(hits, 1, float) / np.arange(1, hits.shape[1] + 1)
    return ds.Array(prec.sum(1) / relevant.shape[1])


def mean_average_precision(
    relevant: ds.IDense, ranking: ds.IDense, *, at: int = 0
) -> float:
    return average_precision(relevant, ranking).mean()[0]


ap = average_precision
map = mean_average_precision

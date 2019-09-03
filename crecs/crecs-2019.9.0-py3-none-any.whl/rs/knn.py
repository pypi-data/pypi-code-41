# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

from typing import Any, Callable

import numpy as np
import scipy.sparse as sp
from implicit._nearest_neighbours import NearestNeighboursScorer, all_pairs_knn

from crecs import ds, sage
from crecs.rs.abc import SparseScorerModel, ZeroOrMore
from crecs.rs.base import BaseSparseScorer


WeightFn = Callable[[sp.spmatrix], sp.spmatrix]


class CollabItemKNNModel(SparseScorerModel):
    def __init__(self, consumed: ds.DSparse, similarity: ds.DSparse):
        self.consumed = consumed
        self.similarity = similarity

    def predict_scores(
        self, users: ZeroOrMore[int] = None, items: ZeroOrMore[int] = None
    ) -> ds.FSparse:
        consumed = ds.slice(self.consumed, users, items)
        similarity = ds.slice(self.similarity, items, items)
        return (consumed @ similarity).as_type(np.float32)


DST = ds.SparseDataset[np.float64]


class CollabItemKNN(BaseSparseScorer[DST]):
    def __init__(
        self,
        k: int = 20,
        weight_fn: WeightFn = None,
        show_progress: bool = True,
        num_threads: int = 0,
    ):
        self.k = k
        self.weight_fn = (lambda x: x) if weight_fn is None else weight_fn
        self.show_progress = show_progress
        self.num_threads = num_threads

    def __call__(self, dataset: DST) -> CollabItemKNNModel:
        weighted = self.weight_fn(dataset._data.T)
        out: sp.csr_matrix = all_pairs_knn(weighted, self.k).tocsr()
        similarity = ds.matrix(out, np.float64)
        return CollabItemKNNModel(dataset.data, similarity)

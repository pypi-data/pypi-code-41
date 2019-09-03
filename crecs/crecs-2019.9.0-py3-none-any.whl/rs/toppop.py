# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

from typing import Any

import numpy as np

from crecs import ds
from crecs.rs import abc
from crecs.rs.utils import get_n_users


class TopPopModel(abc.RecommenderModel):
    def __init__(self, n_users: int, n_items: int, pop: np.ndarray):
        self.n_users = n_users
        self.n_items = n_items
        self.pop = pop

    def recommend(
        self,
        users: abc.UsersT = None,
        items: abc.ZeroOrMore[int] = None,
        n: int = None,
    ) -> ds.IDense:
        n_users = get_n_users(users, self.n_users)
        return ds.DenseMatrix(np.tile(self.pop[:n], (n_users, 1)))


def fit(dataset: ds.Sparse[Any]) -> TopPopModel:
    m: np.ndarray = dataset._data.astype(bool).sum(axis=0, dtype=np.int32)
    m = m.view(np.ndarray).reshape(-1)
    pop = m.argsort()[::-1]

    return TopPopModel(*dataset.shape, pop)

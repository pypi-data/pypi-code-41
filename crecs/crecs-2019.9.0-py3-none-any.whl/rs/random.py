# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

from functools import partial
from typing import Any, Sequence, Union, cast

import numpy as np

from crecs import ds
from crecs.rs import abc
from crecs.rs.utils import get_n_users


class RandomModel(abc.DenseScorerModel, abc.RecommenderModel):
    def __init__(self, n_users: int, n_items: int):
        self.n_users = n_users
        self.n_items = n_items

    def predict_scores(
        self,
        users: abc.ZeroOrMore[int] = None,
        items: abc.ZeroOrMore[int] = None,
    ) -> ds.FDense:
        users = ds.to_sequence(users)
        items = ds.to_sequence(items)

        n_users = len(users) if users else self.n_users
        n_items = len(items) if items else self.n_items

        return ds.DenseMatrix(np.random.rand(n_users, n_items))

    def recommend(
        self,
        users: abc.UsersT = None,
        items: abc.ZeroOrMore[int] = None,
        n: int = None,
    ) -> ds.IDense:

        n_users = get_n_users(users, self.n_users)

        if not isinstance(users, ds.Dataset):
            items = ds.to_sequence(items)
            items, len_items = (  # type: ignore
                (items, len(items)) if items else (self.n_items, self.n_items)
            )
            get_items = lambda u: items
        else:
            # FIXME we need to handle the differences between int and int32/64
            get_items = partial(filter_consumed_items, users)  # type: ignore
            len_items = users.n_items

        n = n or len_items
        assert n <= len_items

        out = np.full((n_users, n), -1, np.int32)

        for u in range(n_users):
            u_it = get_items(u)
            size = min(u_it if isinstance(u_it, int) else len(u_it), n)
            out[u, :size] = np.random.choice(u_it, size=size, replace=False)

        return ds.DenseMatrix(out)


def filter_consumed_items(
    dataset: ds.SparseDataset[Any], user: int
) -> ds.Array[np.int32]:
    consumed = dataset._data
    return ds.Array(np.delete(dataset.item_ids, consumed[user].indices))


def fit(dataset: ds.SparseDataset[Any]) -> RandomModel:
    return RandomModel(dataset.n_users, dataset.n_items)

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = [
    "BaseRecommender",
    "BaseScorer",
    "BaseDenseScorer",
    "BaseSparseScorer",
    "ScorerRecommenderModel",
    "ScorerRecommender",
]

from typing import Callable, Generic, Sequence, TypeVar, Union

from crecs import ds, sage
from crecs.rs import abc
from crecs.rs.abc import D, P

S = TypeVar("S")


# TODO: we could use ds.Sparse instead of D for BaseRecommender
class BaseRecommender(abc.Recommender[D]):
    @classmethod
    def load_recommender(cls, data: sage.HP) -> abc.Recommender[D]:
        return cls(**sage.load_params(cls, data))  # type: ignore


class BaseScorer(abc.Scorer[D, P]):
    @classmethod
    def load_scorer(cls, data: sage.HP) -> abc.Scorer[D, P]:
        return cls(**sage.load_params(cls, data))  # type: ignore

    @classmethod
    def load_recommender(cls, data: sage.HP) -> abc.Recommender[D]:
        return ScorerRecommender(cls.load_scorer(data))


BaseDenseScorer = BaseScorer[D, abc.Ds]
BaseSparseScorer = BaseScorer[D, abc.Sp]


class ScorerRecommenderModel(abc.RecommenderModel, Generic[P]):
    def __init__(self, scorer_model: abc.ScorerModel[P]):
        self.scorer_model: abc.ScorerModel[P] = scorer_model

    def recommend(
        self,
        users: abc.UsersT = None,
        items: abc.ZeroOrMore[int] = None,
        n: int = None,
    ) -> ds.IDense:
        if not isinstance(users, ds.Dataset):
            u = users
        else:
            u = users.user_ids
            items = users.item_ids

        n = n or 10  # FIXME

        scores = self.scorer_model.predict_scores(u, items)

        if isinstance(users, ds.Matrix):
            ds.mask(scores, users)
        return ds.rank(scores, n)


class ScorerRecommender(abc.Recommender[abc.D], Generic[abc.D, P]):
    def __init__(self, scorer: abc.Scorer[abc.D, P]):
        self.scorer: abc.Scorer[abc.D, P] = scorer

    def __call__(self, dataset: abc.D) -> ScorerRecommenderModel[P]:
        return ScorerRecommenderModel(self.scorer(dataset))

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = [
    "Recommender",
    "Scorer",
    "DenseScorer",
    "SparseScorer",
    "RecommenderModel",
    "ScorerModel",
    "DenseScorerModel",
    "SparseScorerModel",
]

import abc
from typing import Any, Dict, Generic, Sequence, Type, TypeVar, Union, overload
from typing_extensions import Protocol, runtime

import numpy as np
import scipy.sparse as sp

from crecs import ds
from crecs.ds.abc import P, Ds, Sp

D = TypeVar("D", contravariant=True)
O = TypeVar("O", covariant=True)


class Fitter(Protocol[D, O]):
    @abc.abstractmethod
    def __call__(self, dataset: D) -> O:
        raise NotImplementedError


S = TypeVar("S")

ZeroOrMore = Union[None, S, Sequence[S]]
UsersT = Union[ZeroOrMore[int], ds.Dataset[Any, Any]]


class RecommenderModel(abc.ABC):
    """
    A RecommenderModel represents a trained recsys ready to provide
    recommendations. It is usually obtained by calling `Recommender.fit`:

        >>> dataset = Dataset(viewed_movies)
        >>> model = recommender.fit(dataset)
    """

    # FIXME: change Dataset[Any, Any] to Sparse[Any]
    @overload
    def recommend(
        self, users: ds.Dataset[Any, Any], items: None = ..., *, n: int = ...
    ) -> ds.IDense:
        pass

    @overload
    def recommend(
        self,
        users: ZeroOrMore[int] = None,
        items: ZeroOrMore[int] = None,
        *,
        n: int = None,
    ) -> ds.IDense:
        pass

    @abc.abstractmethod
    def recommend(
        self,
        users: UsersT = None,
        items: ZeroOrMore[int] = None,
        *,
        n: int = None,
    ) -> ds.IDense:
        """
        Get recommendations for user with id 12:

            >>> model.recommend(12, n=10)

        Get recommendations for users with id [1, 2, 3]:

            >>> model.recommend([1,2,3], n=10)

        Get recommendations for users with id [1, 2, 3] considering only the first
        100 items in the dataset:

            >>> model.recommend([1, 2, 3], dataset.items[:100])

        Get recommendations for the first 50 users in the dataset, excluding the
        items they already consumed (i.e. already viewed movies):

            >>> first100 = dataset[:100, :]
            >>> model.recommend(first100)

        """
        raise NotImplementedError


# NOTE: using a class instead of declaring Recommender as Callable[...], makes
# it possible to subclass it. This is useful because mypy will complain if
# the __call__ method has the wrong signature. At the same time, the fact that
# Recommender is a Protocol means that subclassing it is not mandatory.
class Recommender(Fitter[D, RecommenderModel], Protocol[D]):
    """
    A Recommender is an object capable of constructing a RecommenderModel given
    an appropriate training dataset.
    """

    @abc.abstractmethod
    def __call__(self, __dataset: D) -> RecommenderModel:
        raise NotImplementedError


class ScorerModel(Generic[P]):
    @abc.abstractmethod
    def predict_scores(
        self, users: ZeroOrMore[int] = None, items: ZeroOrMore[int] = None
    ) -> ds.Matrix[P, np.float32]:
        raise NotImplementedError


SparseScorerModel = ScorerModel[Sp]
DenseScorerModel = ScorerModel[Ds]


class Scorer(Fitter[D, ScorerModel[P]], Protocol[D, P]):
    pass


# class Scorer(Generic[D, P]):
#     @abc.abstractmethod
#     def fit_scorer(self, dataset: D) -> ScorerModel[P]:
#         raise NotImplementedError
#

SparseScorer = Scorer[D, Sp]
DenseScorer = Scorer[D, Ds]

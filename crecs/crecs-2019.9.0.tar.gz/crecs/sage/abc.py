# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["RecommenderLoader", "ScorerLoader", "DatasetLoader", "HP"]

import abc
from typing import Any, Dict, TypeVar, Union
from typing_extensions import Protocol, runtime

from crecs import rs
from crecs.rs.abc import D, P, O


SimpleT = Union[int, float, str]
HP = Dict[str, SimpleT]


@runtime
class RecommenderLoader(Protocol[D]):
    @abc.abstractmethod
    def load_recommender(self, data: HP) -> rs.Recommender[D]:
        raise NotImplementedError


@runtime
class RecommenderModelSaver(Protocol):
    @abc.abstractmethod
    def save_recommender(self, rec: rs.RecommenderModel) -> None:
        raise NotImplementedError


@runtime
class ScorerLoader(Protocol[D, P]):
    @abc.abstractmethod
    def load_scorer(self, data: HP) -> rs.Scorer[D, P]:
        raise NotImplementedError


T = TypeVar("T", covariant=True)


@runtime
class DatasetLoader(Protocol[T]):
    @abc.abstractmethod
    def load_dataset(self, data: HP) -> T:
        raise NotImplementedError

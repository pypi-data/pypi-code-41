# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["Visitor"]

import abc
from typing import Any, Callable, Generic, Type, TypeVar

from typing_extensions import Protocol

from crecs.ds.abc import Sparse, Dense, DType


T = TypeVar("T", covariant=True)


class Visitor(Protocol[DType, T]):
    @abc.abstractmethod
    def visit_dense(self, matrix: Dense[DType]) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_sparse(self, matrix: Sparse[DType]) -> T:
        raise NotImplementedError


# class Visitor(Protocol[S]):
#     @abc.abstractmethod
#     def visit_dense(self, matrix: mat.Ds[S]) -> mat.Ds[S]:
#         raise NotImplementedError
#
#     @abc.abstractmethod
#     def visit_sparse(self, matrix: mat.Sp[S]) -> mat.Sp[S]:
#         raise NotImplementedError
#

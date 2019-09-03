# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["matrix"]

from typing import Any, List, Union, Type, TypeVar, overload

from crecs.ds.abc import DType, Dense, Ds, Sp, Sparse
from crecs.ds.dense import DenseMatrix
from crecs.ds.sparse import SparseMatrix

import numpy as np


@overload
def matrix(matrix: List[List[int]], dtype: None = ...) -> Dense[np.int64]:
    pass


@overload
def matrix(matrix: List[List[float]], dtype: None = ...) -> Dense[np.float64]:
    pass


@overload
def matrix(matrix: List[List[Any]], dtype: Type[DType]) -> Dense[DType]:
    pass


@overload
def matrix(matrix: Ds, dtype: Type[DType]) -> Dense[DType]:
    pass


@overload
def matrix(matrix: Sp, dtype: Type[DType]) -> Sparse[DType]:
    pass


def matrix(
    matrix: Union[Ds, Sp, List[List[Any]]], dtype: Type[DType] = None
) -> Union[Sparse[DType], Dense[DType]]:
    if isinstance(matrix, Sp):
        return SparseMatrix(matrix, dtype)

    if isinstance(matrix, list):
        matrix = np.array(matrix, dtype=dtype)
    return DenseMatrix(matrix)

# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = [
    "Array",
    "is_dense",
    "is_sparse",
    "are_compatible",
    "to_sequence",
    "slice",
    "rank",
    "mask",
]

from typing import Any, Generic, Sequence, Type, TypeVar, Union

import numpy as np

from crecs.ds import abc
from crecs.ds.abc import Matrix, Ds, Sp, P, DType
from crecs.ds.visitor import Visitor


def is_dense(x: Any) -> bool:
    return isinstance(x, Matrix) and isinstance(x._data, Ds)


def is_sparse(x: Any) -> bool:
    return isinstance(x, Matrix) and isinstance(x._data, Sp)


def are_compatible(a: abc.BaseMatrix[Any, Any, Any], b: Any) -> bool:
    return isinstance(b, a.interface) and a.backend is b.backend


S = TypeVar("S")
T = TypeVar("T")

ZeroOrMore = Union[None, T, Sequence[T]]


class Array(np.ndarray, Sequence[DType], Generic[DType]):
    """
    A numpy array that ensures ndim always equals 1.

    NOTE: unlike a numpy ndarray this class subclasses Sequence and thus gains
    some mixin methods such as index and count. This makes instances usable
    as type Sequence[T] unlike numpy arrays.
    """

    def __new__(cls: Type[S], input: Any) -> S:
        return np.asanyarray(input).view(cls)

    def __array_finalize__(self, obj: Any) -> None:
        if self.ndim != 1:
            self.shape = (self.size,)

    def __bool__(self) -> bool:
        return len(self) != 0


def to_sequence(x: ZeroOrMore[T] = None) -> Sequence[T]:
    if x is None:
        return ()

    return x if isinstance(x, Sequence) else (x,)


def slice(
    mat: Matrix[P, DType], x: ZeroOrMore[int] = None, y: ZeroOrMore[int] = None
) -> Matrix[P, DType]:
    a = to_sequence(x)
    b = to_sequence(y)

    # NOTE instances of Array cannot be used with np.ix_
    a = a.view(np.ndarray) if isinstance(a, Array) else a  # type: ignore
    b = b.view(np.ndarray) if isinstance(b, Array) else b  # type: ignore

    if len(a) == 0:
        return mat[:, b] if y else mat
    if len(b) == 0:
        return mat[a, :]

    z = mat[a, :]
    return z[:, b]


class RankVisitor(Visitor[np.float32, abc.IDense]):
    def __init__(self, n: int):
        self.n = n

    def visit_dense(self, matrix: abc.FDense) -> abc.IDense:
        raise NotImplementedError

    def visit_sparse(self, matrix: abc.FSparse) -> abc.IDense:
        from crecs.ds.dense import DenseMatrix  # NOTE: avoid circular import

        a = matrix._data
        m = a.shape[0]
        n = self.n
        out = np.zeros((m, n), int)

        j = 0
        for i in range(m):
            k = a.indptr[i + 1]

            idx = a.data[j:k].argsort()[:n] + j
            out[i, : len(idx)] = a.indices[idx]

            j = k
        return DenseMatrix(out)


def rank(matrix: abc.Matrix[P, np.float32], n: int) -> abc.IDense:
    return matrix.accept(RankVisitor(n))


class MaskVisitor(Visitor[DType, None], Generic[DType]):
    def __init__(self, mask: abc.Sparse[DType]):
        self.mask: abc.Sparse[DType] = mask

    def visit_dense(self, matrix: abc.Dense[DType]) -> None:
        mat = self.mask._data
        out = matrix._data
        # assert isinstance(mat, sp.csr_matrix)

        i = 0
        for row, j in enumerate(mat.indptr[1:]):
            indices = mat.indices[i:j]
            out[row, indices] = 0
            i = j
        out.eliminate_zeros()

    def visit_sparse(self, matrix: abc.Sparse[DType]) -> None:
        diff = matrix * self.mask
        matrix._data -= diff._data
        matrix._data.eliminate_zeros()


def mask(matrix: abc.Matrix[P, DType], mask: abc.Sparse[DType]) -> None:
    matrix.accept(MaskVisitor(mask))

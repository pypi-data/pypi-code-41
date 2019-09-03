# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["DenseMatrix"]

from typing import Any, Generic, Tuple, Type

import numpy as np
import scipy.sparse as sp

from crecs.ds import abc, common, utils
from crecs.ds.abc import (
    Dense,
    DenseRow,
    DenseCol,
    Ds,
    DType,
    DType2,
    Sparse,
    SparseRow,
    SparseCol,
)
from crecs.ds.common import C
from crecs.ds.visitor import Visitor, T


class DenseCommon(common.CommonBase[C, Ds, DType], Generic[C, DType]):
    @property
    def backend(self) -> Type[Ds]:
        return Ds

    def __mul__(self: C, other: C) -> C:
        # elementwise multiplication
        return (
            self.with_data(self._data * other._data)
            if type(self) is type(other)
            else NotImplemented
        )

    def __rmul__(self: C, other: C) -> C:
        return (
            other.with_data(other._data * self._data)
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    def to_dense(self: C) -> C:
        return self

    def __eq__(self, other: Any) -> bool:
        try:
            data = other._data
        except AttributeError:
            data = None

        if not isinstance(data, np.ndarray):
            return NotImplemented

        return np.all(self._data == data)

    def __repr__(self) -> str:
        name = self.__class__.__name__
        dt = self._data.dtype.name
        shape = common.format_shape(self.shape)
        return f"<{name}[{dt}] shape: {shape}>"


class DRow(DenseCommon["DRow[DType]", DType], DenseRow[DType], Generic[DType]):
    @property
    def interface(self) -> Type[abc.Row[Any, Any]]:
        return abc.Row

    @property
    def at(self) -> abc.ValuesIndexer1D[DType]:
        return common.CommonRowValuesIndexer(self._data)

    def __getitem__(self, x: Any) -> DenseRow[DType]:
        return self._data[x]

    # def __setitem__(self, x: int, val: DType) -> None:
    #    self._data[x] = val

    def __matmul__(self, other: DenseCol[DType]) -> DType:
        return self._data @ other._data

    def to_sparse(self) -> SparseRow[DType]:
        return sparse.SRow(sp.csr_matrix(self._data))

    def as_type(self, t: Type[DType2]) -> DenseRow[DType2]:
        return self.__class__(self._data.astype(t))  # type: ignore


class DCol(DenseCommon["DCol[DType]", DType], DenseCol[DType], Generic[DType]):
    @property
    def interface(self) -> Type[abc.Col[Any, Any]]:
        return abc.Col

    @property
    def at(self) -> abc.ValuesIndexer1D[DType]:
        return common.CommonColValuesIndexer(self._data)

    def __getitem__(self, x: Any) -> DenseCol[DType]:
        return self._data[x]

    # def __setitem__(self, x: int, val: DType) -> None:
    #    self._data[x] = val

    def __matmul__(self, other: DenseRow[DType]) -> Dense[DType]:
        return DenseMatrix(self._data @ other._data)

    def __rmatmul__(self, other: Dense[DType]) -> DenseCol[DType]:
        return self.__class__(self._data @ other._data)

    def to_sparse(self) -> SparseCol[DType]:
        return sparse.SCol(sp.csr_matrix(self._data))

    def as_type(self, t: Type[DType2]) -> DenseCol[DType2]:
        return self.__class__(self._data.astype(t))  # type: ignore


class DenseRowsIndexer(abc.RowsIndexer[Ds, DType], Generic[DType]):
    def __init__(self, data: Ds):
        self._data = data

    def __getitem__(self, idx: int) -> DenseRow[DType]:
        return DRow(self._data[idx].reshape(1, -1))

    def __setitem__(self, idx: int, val: DenseRow[DType]) -> None:
        self._data[idx] = val._data


class DenseColsIndexer(abc.ColsIndexer[Ds, DType], Generic[DType]):
    def __init__(self, data: Ds):
        self._data = data

    def __getitem__(self, idx: int) -> DenseCol[DType]:
        return DCol(self._data[:, idx].reshape(-1, 1))

    def __setitem__(self, idx: int, val: DenseCol[DType]) -> None:
        self._data[:, idx] = val._data


class DenseMatrix(
    DenseCommon["DenseMatrix[DType]", DType], Dense[DType], Generic[DType]
):
    @property
    def interface(self) -> Type[abc.Matrix[Any, Any]]:
        return abc.Matrix

    def __getitem__(self, other: Tuple[Any, Any]) -> "DenseMatrix[DType]":
        return self.__class__(self._data[other])

    @property
    def at(self) -> abc.ValuesIndexer2D[DType]:
        return common.CommonValuesIndexer(self._data)

    @property
    def rows(self) -> abc.RowsIndexer[Ds, DType]:
        return DenseRowsIndexer(self._data)

    @property
    def cols(self) -> abc.ColsIndexer[Ds, DType]:
        return DenseColsIndexer(self._data)

    def to_sparse(self) -> Sparse[DType]:
        return sparse.SparseMatrix(sp.csr_matrix(self._data))

    def as_type(self, t: Type[DType2]) -> Dense[DType2]:
        return self.__class__(self._data.astype(t))  # type: ignore

    def __matmul__(self, other: Dense[DType]) -> Dense[DType]:
        return (
            self.with_data(self._data @ other._data)
            if type(self) is type(other)
            else NotImplemented
        )

    def __rmatmul__(self, other: Dense[DType]) -> Dense[DType]:
        return (
            other.with_data(other._data @ self._data)
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    def accept(self, visitor: Visitor[DType, T]) -> T:
        return visitor.visit_dense(self)


from crecs.ds import sparse

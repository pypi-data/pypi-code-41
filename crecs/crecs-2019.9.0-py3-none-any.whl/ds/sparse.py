# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["SparseMatrix"]

from typing import Any, Generic, Tuple, Type

import scipy.sparse as sp

from crecs.ds import abc, common, utils
from crecs.ds.abc import (
    Dense,
    DenseRow,
    DenseCol,
    DType,
    DType2,
    Sparse,
    SparseRow,
    SparseCol,
    Sp,
)
from crecs.ds.common import C
from crecs.ds.visitor import Visitor, T


class SparseCommon(common.CommonBase[C, Sp, DType], Generic[C, DType]):
    @property
    def backend(self) -> Type[Sp]:
        return Sp

    def __mul__(self: C, other: C) -> C:
        # elementwise multiplication
        return (
            self.with_data(self._data.multiply(other._data))
            if type(self) is type(other)
            else NotImplemented
        )

    def __rmul__(self: C, other: C) -> C:
        return (
            other.with_data(other._data.multiply(self._data))
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    def to_sparse(self: C) -> C:
        return self

    def __eq__(self, other: Any) -> bool:
        try:
            data = other._data
        except AttributeError:
            data = None

        if not isinstance(data, sp.csr_matrix):
            return NotImplemented

        return (self._data != data).nnz == 0

    def __repr__(self) -> str:
        name = self.__class__.__name__
        dt = self._data.dtype.name
        shape = common.format_shape(self.shape)
        nnz = self._data.nnz
        density = nnz * 100 / (self.shape[0] * self.shape[1])
        return (
            f"<{name}[{dt}] shape: {shape} | nnz: {nnz:,} "
            f"| density: {density:07.4f}%>"
        )


class SRow(
    SparseCommon["SRow[DType]", DType], SparseRow[DType], Generic[DType]
):
    @property
    def interface(self) -> Type[abc.Row[Any, Any]]:
        return abc.Row

    @property
    def at(self) -> abc.ValuesIndexer1D[DType]:
        return common.CommonRowValuesIndexer(self._data)

    def __getitem__(self, x: Any) -> SparseRow[DType]:
        return self._data[x]

    def __matmul__(self, other: SparseCol[DType]) -> DType:
        return self._data @ other._data

    def to_dense(self) -> DenseRow[DType]:
        return dense.DRow(self._data.todense())

    def as_type(self, t: Type[DType2]) -> SparseRow[DType2]:
        return self.__class__(self._data.astype(t))  # type: ignore


class SCol(
    SparseCommon["SCol[DType]", DType], SparseCol[DType], Generic[DType]
):
    @property
    def interface(self) -> Type[abc.Col[Any, Any]]:
        return abc.Col

    @property
    def at(self) -> abc.ValuesIndexer1D[DType]:
        return common.CommonColValuesIndexer(self._data)

    def __getitem__(self, x: Any) -> SparseCol[DType]:
        return self._data[x]

    def __matmul__(self, other: SparseRow[DType]) -> Sparse[DType]:
        return SparseMatrix(self._data @ other._data)

    def __rmatmul__(self, other: Sparse[DType]) -> SparseCol[DType]:
        return self.__class__(self._data @ other._data)

    def to_dense(self) -> DenseCol[DType]:
        return dense.DCol(self._data.todense())

    def as_type(self, t: Type[DType2]) -> SparseCol[DType2]:
        return self.__class__(self._data.astype(t))  # type: ignore


class SparseRowsIndexer(abc.RowsIndexer[Sp, DType], Generic[DType]):
    def __init__(self, data: Sp):
        self._data = data

    def __getitem__(self, idx: int) -> SparseRow[DType]:
        return SRow(self._data.getrow(idx))

    def __setitem__(self, idx: int, val: SparseRow[DType]) -> None:
        self._data[idx] = val._data


class SparseColsIndexer(abc.ColsIndexer[Sp, DType], Generic[DType]):
    def __init__(self, data: Sp):
        self._data = data

    def __getitem__(self, idx: int) -> SparseCol[DType]:
        return SCol(self._data.getcol(idx))

    def __setitem__(self, idx: int, val: SparseCol[DType]) -> None:
        self._data[:, idx] = val._data


class SparseMatrix(
    SparseCommon["SparseMatrix[DType]", DType], Sparse[DType], Generic[DType]
):
    @property
    def interface(self) -> Type[abc.Matrix[Any, Any]]:
        return abc.Matrix

    def __getitem__(self, other: Tuple[Any, Any]) -> "SparseMatrix[DType]":
        return self.__class__(self._data[other])

    @property
    def at(self) -> abc.ValuesIndexer2D[DType]:
        return common.CommonValuesIndexer(self._data)

    @property
    def rows(self) -> abc.RowsIndexer[Sp, DType]:
        return SparseRowsIndexer(self._data)

    @property
    def cols(self) -> abc.ColsIndexer[Sp, DType]:
        return SparseColsIndexer(self._data)

    def to_dense(self) -> Dense[DType]:
        return dense.DenseMatrix(self._data.todense())

    def as_type(self, t: Type[DType2]) -> Sparse[DType2]:
        return self.__class__(self._data.astype(t))  # type: ignore

    def __matmul__(self, other: Sparse[DType]) -> Sparse[DType]:
        return (
            self.with_data(self._data @ other._data)
            if type(self) is type(other)
            else NotImplemented
        )

    def __rmatmul__(self, other: Sparse[DType]) -> Sparse[DType]:
        return (
            other.with_data(other._data @ self._data)
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    def accept(self, visitor: Visitor[DType, T]) -> T:
        return visitor.visit_sparse(self)


from crecs.ds import dense

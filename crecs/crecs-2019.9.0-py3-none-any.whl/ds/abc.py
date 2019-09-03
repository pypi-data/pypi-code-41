# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = [
    "DType",
    "Matrix",
    "Row",
    "Col",
    "Dense",
    "DenseRow",
    "DenseCol",
    "Sparse",
    "SparseRow",
    "SparseCol",
    "FDense",
    "DDense",
    "IDense",
    "LDense",
    "FSparse",
    "DSparse",
    "ISparse",
    "LSparse",
]

import abc
from typing import (
    Any,
    Generic,
    NewType,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
    TYPE_CHECKING,
)

import numpy as np
import scipy.sparse as sp


if TYPE_CHECKING:
    from crecs.ds.visitor import Visitor

double = np.float64

DType = TypeVar(
    "DType",
    bool,
    np.int8,
    np.int16,
    np.int32,
    np.int64,
    np.uint8,
    np.uint16,
    np.uint32,
    np.uint64,
    np.float16,
    np.float32,
    np.float64,
)

DType2 = TypeVar(
    "DType2",
    bool,
    np.int8,
    np.int16,
    np.int32,
    np.int64,
    np.uint8,
    np.uint16,
    np.uint32,
    np.uint64,
    np.float16,
    np.float32,
    np.float64,
)
X = TypeVar("X")


Sp = sp.csr_matrix  # NewType("Sp", _Phantom)
Ds = np.ndarray  # NewType("Ds", _Phantom)
P = TypeVar("P", Sp, Ds)
P2 = TypeVar("P2", Sp, Ds)

M = TypeVar("M", bound="Matrix[Any, Any]")

B = TypeVar("B")
T = TypeVar("T", covariant=True)


class BaseMatrix(Generic[B, P, DType]):

    _data: P

    # FIXME it would be nice if this could be a class property
    @property
    @abc.abstractmethod
    def backend(self) -> Type[P]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def interface(
        self
    ) -> Type[Union["Matrix[Any, Any]", "Row[Any, Any]", "Col[Any, Any]"]]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def dtype(self) -> Type[DType]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def shape(self) -> Tuple[int, int]:
        raise NotImplementedError

    @abc.abstractmethod
    def with_data(self, data: P) -> B:
        raise NotImplementedError

    @abc.abstractmethod
    def __add__(self, other: B) -> B:
        raise NotImplementedError

    @abc.abstractmethod
    def __sub__(self, other: B) -> B:
        raise NotImplementedError

    @abc.abstractmethod
    def __mul__(self, other: B) -> B:
        raise NotImplementedError

    @abc.abstractmethod
    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def max(self) -> DType:
        raise NotImplementedError

    @abc.abstractmethod
    def min(self) -> DType:
        raise NotImplementedError

    @abc.abstractmethod
    def sum(self) -> DType:
        raise NotImplementedError


# TODO: add .T
class Matrix(BaseMatrix["Matrix[P, DType]", P, DType], Generic[P, DType]):
    """
    We need the type parameter P to make Sparse and Dense matrices not
    interoperable. The following code should not typecheck:

        >>> a: Matrix[int] = Dense(..)
        >>> b: Matrix[int] = Sparse(..)
        >>> a @ b
    """

    @property
    @abc.abstractmethod
    def at(self) -> "ValuesIndexer2D[DType]":
        raise NotImplementedError

    ## NOTE: Change this to matrix.rows[10], matrix.rows[10] = row
    @property
    @abc.abstractmethod
    def rows(self) -> "RowsIndexer[P, DType]":
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def cols(self) -> "ColsIndexer[P, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def to_dense(self) -> "Matrix[Ds, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def to_sparse(self) -> "Matrix[Sp, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, other: Tuple[Any, Any]) -> "Matrix[P, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def __matmul__(self, other: "Matrix[P, DType]") -> "Matrix[P, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def as_type(self, t: Type[DType2]) -> "Matrix[P, DType2]":
        raise NotImplementedError

    # @abc.abstractmethod
    # def transform(self, transformer: "Transformer[DType, X]") -> X:
    #     raise NotImplementedError

    @abc.abstractmethod
    def accept(self, visitor: "Visitor[DType, T]") -> T:
        raise NotImplementedError


class ValuesIndexer2D(Generic[DType]):
    @abc.abstractmethod
    def __getitem__(self, idx: Tuple[int, int]) -> DType:
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, idx: Tuple[int, int], val: DType) -> None:
        raise NotImplementedError


class ValuesIndexer1D(Generic[DType]):
    @abc.abstractmethod
    def __getitem__(self, idx: int) -> DType:
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, idx: int, val: DType) -> None:
        raise NotImplementedError


# 1xN
class Row(BaseMatrix["Row[P, DType]", P, DType], Generic[P, DType]):
    @property
    @abc.abstractmethod
    def at(self) -> ValuesIndexer1D[DType]:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, x: Any) -> "Row[P, DType]":
        raise NotImplementedError

    # @abc.abstractmethod
    # def __setitem__(self, x: Any, val: DType) -> None:
    #    raise NotImplementedError

    @abc.abstractmethod
    def __matmul__(self, other: "Col[P, DType]") -> DType:
        pass

    @abc.abstractmethod
    def to_dense(self) -> "Row[Ds, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def to_sparse(self) -> "Row[Sp, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def as_type(self, t: Type[DType2]) -> "Row[P, DType2]":
        raise NotImplementedError


class RowsIndexer(Generic[P, DType]):
    @abc.abstractmethod
    def __getitem__(self, idx: int) -> Row[P, DType]:
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, idx: int, val: Row[P, DType]) -> None:
        raise NotImplementedError


# Nx1
class Col(BaseMatrix["Col[P, DType]", P, DType], Generic[P, DType]):
    @property
    @abc.abstractmethod
    def at(self) -> ValuesIndexer1D[DType]:
        raise NotImplementedError

    @abc.abstractmethod
    def __getitem__(self, x: Any) -> "Col[P, DType]":
        raise NotImplementedError

    # @abc.abstractmethod
    # def __setitem__(self, x: Any, val: DType) -> None:
    #    raise NotImplementedError

    @abc.abstractmethod
    def __matmul__(self, other: "Row[P, DType]") -> "Matrix[P, DType]":
        pass

    @abc.abstractmethod
    def __rmatmul__(self, other: "Matrix[P, DType]") -> "Col[P, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def to_dense(self) -> "Col[Ds, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def to_sparse(self) -> "Col[Sp, DType]":
        raise NotImplementedError

    @abc.abstractmethod
    def as_type(self, t: Type[DType2]) -> "Col[P, DType2]":
        raise NotImplementedError


class ColsIndexer(Generic[P, DType]):
    @abc.abstractmethod
    def __getitem__(self, idx: int) -> Col[P, DType]:
        raise NotImplementedError

    @abc.abstractmethod
    def __setitem__(self, idx: int, val: Col[P, DType]) -> None:
        raise NotImplementedError


# FMat = Matrix[P, float]
# IMat = Matrix[P, int]


Dense = Matrix[Ds, DType]
DenseRow = Row[Ds, DType]
DenseCol = Col[Ds, DType]
FDense = Dense[np.float32]
DDense = Dense[np.float64]
IDense = Dense[np.int32]
LDense = Dense[np.int64]

Sparse = Matrix[Sp, DType]
SparseRow = Row[Sp, DType]
SparseCol = Col[Sp, DType]
FSparse = Sparse[np.float32]
DSparse = Sparse[np.float64]
ISparse = Sparse[np.int32]
LSparse = Sparse[np.int64]

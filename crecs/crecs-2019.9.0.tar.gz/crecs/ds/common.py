# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

from abc import abstractmethod
from typing import Any, Generic, Tuple, Type, TypeVar, cast, overload

from crecs.ds import abc, utils
from crecs.ds.abc import BaseMatrix, DType, P

C = TypeVar("C", bound="CommonBase[Any, Any, Any]")


class CommonBase(BaseMatrix[C, P, DType], Generic[C, P, DType]):
    __array_ufunc__ = None

    def __init__(self, data: P, dtype: Type[DType] = None):
        if dtype is not None:
            data = data.astype(dtype, copy=False)
        self._data = data

    @property
    def dtype(self) -> Type[DType]:
        return cast(Type[DType], self._data.dtype.type)

    @property
    def shape(self) -> Tuple[int, int]:
        return cast(Tuple[int, int], self._data.shape)

    def with_data(self: C, data: P) -> C:
        # XXX check dtype?
        return self.__class__(data)

    def __add__(self: C, other: C) -> C:
        return (
            self.with_data(self._data + other._data)
            if type(self) is type(other)
            else NotImplemented
        )

    def __radd__(self: C, other: C) -> C:
        return (
            other.with_data(other._data + self._data)
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    def __sub__(self: C, other: C) -> C:
        return (
            self.with_data(self._data - other._data)
            if type(self) is type(other)
            else NotImplemented
        )

    def __rsub__(self: C, other: C) -> C:
        return (
            other.with_data(other._data - self._data)
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    def max(self) -> DType:
        return self._data.max()

    def min(self) -> DType:
        return self._data.min()

    def sum(self) -> DType:
        return self._data.sum()


class CommonValuesIndexer(abc.ValuesIndexer2D[DType], Generic[P, DType]):
    def __init__(self, data: P):
        self._data: P = data

    def __getitem__(self, idx: Tuple[int, int]) -> DType:
        return self._data[idx]

    def __setitem__(self, idx: Tuple[int, int], val: DType) -> None:
        self._data[idx] = val


class CommonRowValuesIndexer(abc.ValuesIndexer1D[DType], Generic[P, DType]):
    def __init__(self, data: P):
        self._data: P = data

    def __getitem__(self, idx: int) -> DType:
        return self._data[0, idx]

    def __setitem__(self, idx: int, val: DType) -> None:
        self._data[0, idx] = val


class CommonColValuesIndexer(abc.ValuesIndexer1D[DType], Generic[P, DType]):
    def __init__(self, data: P):
        self._data: P = data

    def __getitem__(self, idx: int) -> DType:
        return self._data[idx, 0]

    def __setitem__(self, idx: int, val: DType) -> None:
        self._data[idx, 0] = val


def format_shape(shape: Tuple[int, int]) -> str:
    return "{:,}×{:,}".format(*shape)

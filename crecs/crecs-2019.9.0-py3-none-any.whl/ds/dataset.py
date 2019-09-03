# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2019 Germano Gabbianelli <git@germano.dev>

__all__ = ["Dataset", "SparseDataset", "leave_k_out"]

import warnings
from typing import Any, Generic, Sequence, Tuple, Type, Union

import numpy as np
import scipy.sparse as sp

from crecs.ds import abc, dense, sparse, utils
from crecs.ds.abc import DType, P, P2, DType2
from crecs.ds.visitor import Visitor, T


class Dataset(abc.Matrix[P, DType], Generic[P, DType]):
    # Wrappa una matrice qualunque, non per forza sparsa
    # Add item metadata and user metadata
    data: abc.Matrix[P, DType]
    user_ids: Sequence[int]
    item_ids: Sequence[int]

    def __init__(
        self,
        data: abc.Matrix[P, DType],
        user_ids: Sequence[int] = None,
        item_ids: Sequence[int] = None,
    ):
        self.data = data
        self.user_ids = utils.Array(
            np.arange(data.shape[0]) if user_ids is None else user_ids
        )
        self.item_ids = utils.Array(
            np.arange(data.shape[1]) if item_ids is None else item_ids
        )

    @property
    def n_users(self) -> int:
        return self.data.shape[0]

    @property
    def n_items(self) -> int:
        return self.data.shape[1]

    def _with_data(
        self, data: abc.Matrix[P2, DType2]
    ) -> "Dataset[P2, DType2]":
        # mypy bug
        return type(self)(  # type: ignore
            data, user_ids=self.user_ids, item_ids=self.item_ids
        )

    def with_data(self, data: P) -> "Dataset[P, DType]":
        d = type(self.data)(data)  # type: ignore
        return self._with_data(d)

    def to_sparse(self) -> abc.Sparse[DType]:
        return self._with_data(self.data.to_sparse())

    def to_dense(self) -> abc.Dense[DType]:
        return self._with_data(self.data.to_dense())

    def as_type(self, t: Type[DType2]) -> "Dataset[P, DType2]":
        return self._with_data(self.data.as_type(t))

    def accept(self, visitor: Visitor[DType, T]) -> T:
        return (
            visitor.visit_dense(self)  # type: ignore
            if self.backend is abc.Ds
            else visitor.visit_sparse(self)  # type: ignore
        )

    def __getitem__(self, x: Tuple[Any, Any]) -> "Dataset[P, DType]":
        a, b = x
        return type(self)(self.data[a, b], self.user_ids[a], self.item_ids[b])

    def __repr__(self) -> str:
        return f"<Dataset: {self.data}>"

    def __add__(self, other: abc.Matrix[P, DType]) -> abc.Matrix[P, DType]:
        return NotImplemented

    def __sub__(self, other: abc.Matrix[P, DType]) -> abc.Matrix[P, DType]:
        return NotImplemented

    def __mul__(self, other: abc.Matrix[P, DType]) -> abc.Matrix[P, DType]:
        return NotImplemented

    def __matmul__(self, other: abc.Matrix[P, DType]) -> abc.Matrix[P, DType]:
        return NotImplemented

    def __rmul__(self, other: abc.Matrix[P, DType]) -> abc.Matrix[P, DType]:
        return (
            self._with_data(other * self.data)
            if utils.are_compatible(self, other)
            else NotImplemented
        )

    @property  # type: ignore
    def _data(self) -> P:  # type: ignore
        return self.data._data

    @_data.setter
    def _data(self, val: P) -> None:
        self.data._data = val

    @property
    def backend(self) -> Type[P]:
        return self.data.backend

    @property
    def interface(
        self
    ) -> Type[
        Union[abc.Matrix[Any, Any], abc.Row[Any, Any], abc.Col[Any, Any]]
    ]:
        return self.data.interface

    @property
    def dtype(self) -> Type[DType]:
        return self.data.dtype

    @property
    def shape(self) -> Tuple[int, int]:
        return self.data.shape

    def __eq__(self, other: Any) -> bool:
        return self.data == other

    def max(self) -> DType:
        return self.data.max()

    def min(self) -> DType:
        return self.data.min()

    def sum(self) -> DType:
        return self.data.sum()

    @property
    def at(self) -> abc.ValuesIndexer2D[DType]:
        return self.data.at

    @property
    def rows(self) -> abc.RowsIndexer[P, DType]:
        return self.data.rows

    @property
    def cols(self) -> abc.ColsIndexer[P, DType]:
        return self.data.cols


SparseDataset = Dataset[abc.Sp, DType]


def leave_k_out(
    a: abc.Sparse[DType], k: int = 1, min_train: int = 0, filter: bool = False
) -> Tuple[abc.Sparse[DType], abc.Dense[np.int32]]:

    mat = a._data
    j = mat.indptr[0]

    train_data = np.zeros_like(mat.data)
    train_indices = np.zeros_like(mat.indices)
    train_indptr = np.zeros_like(mat.indptr)

    test = np.full((mat.shape[0], k), -1, np.int32)

    uids = (
        np.zeros(mat.shape[0], bool)
        if filter and isinstance(a, Dataset)
        else None
    )
    out_i = 1
    train_j = 0

    N = len(mat.indptr)
    K = k

    for i in range(1, N):
        k = mat.indptr[i]

        n = k - j
        idx = np.random.permutation(n) + j

        test_n = max(0, min(n, K))
        train_n = max(0, n - test_n)

        if test_n == n or train_n < min_train:
            if filter:
                j = k
                continue
            warnings.warn(f"User {i} has not enough elements ({n})")

        if uids is not None:
            uids[i - 1] = True

        train_k = train_j + train_n
        test_idx = idx[:test_n]
        train_idx = idx[test_n:]

        train_data[train_j:train_k] = mat.data[train_idx]
        train_indices[train_j:train_k] = mat.indices[train_idx]
        train_indptr[out_i] = train_k  # train_indptr[out_i - 1] + train_n

        test[out_i - 1, :test_n] = mat.indices[test_idx]

        out_i += 1
        j = k
        train_j = train_k

    out_shape = (out_i - 1, mat.shape[1])

    train_indptr = train_indptr[:out_i]
    train_nnz = train_indptr[-1]
    train_data = train_data[:train_nnz]
    train_indices = train_indices[:train_nnz]
    train = sp.csr_matrix((train_data, train_indices, train_indptr), out_shape)

    test_out: abc.Dense[np.int32] = dense.DenseMatrix(
        test[: out_i - 1], np.int32
    )
    train_out: abc.Sparse[DType] = sparse.SparseMatrix(train)

    if isinstance(a, Dataset) and uids is not None:
        train_out = Dataset(
            train_out, user_ids=a.user_ids[uids], item_ids=a.item_ids
        )

    return train_out, test_out


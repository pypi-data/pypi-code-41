# -*- coding: utf-8 -*-
"""QAbstractTableModel for 2D arrays module.

contains PSNumpyModel2D
"""

import numpy as np
from PyQt5 import QtCore


class PSNumpyModel2D(QtCore.QAbstractTableModel):

    """Subclass of QAbstractTableModel used to display numpy 2D arrays."""

    def __init__(self, narray: np.ndarray, parent: QtCore.QObject = None):
        """Model init.

        Args:
            narray (numpy.ndarray): 2D numpy array
            parent (QObject): Qt parent, passed to QAbstractTableModel.
                Default: None.
        """
        super().__init__(parent)
        self.__array = narray

    def getRow(self, index: int) -> np.ndarray:
        """Return single row.

        Args:
            index (int): Row index.
        Returns:
            One dimensional numpy.ndarray containing the requested row.
        """
        return self.__array[index, :]

    def getColumn(self, index: int) -> np.ndarray:
        """Return single column.

        Args:
            index (int): Column index.
        Returns:
            One dimensional numpy.ndarray containing the requested column.
        """
        return self.__array[:, index]

    def rowCount(self, parent: QtCore.QObject = None) -> int:
        """Return number of rows.

        Returns:
            Number of rows (int).
        """
        return self.__array.shape[0]

    def columnCount(self, parent: QtCore.QObject = None) -> int:
        """Return number of columns.

        Returns:
            Number of columns (int).
        """
        return self.__array.shape[1]

    def data(self, index: QtCore.QModelIndex,
             role=QtCore.Qt.DisplayRole) -> QtCore.QVariant:
        """Data at `index`.

        Args:
            index (QModelIndex): Table index.
            role (Qt role): Qt role, defaults to Qt.DisplayRole

        Returns:
            QVariant containing the str(data) at `index`.
        """
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                row = index.row()
                col = index.column()
                return QtCore.QVariant(str(self.getItemAt(row, col)))
        return QtCore.QVariant()

    @property
    def array(self) -> np.ndarray:
        """Numpy array underlying this model."""
        return self.__array

    def getItemAt(self, row: int, column: int) -> np.ndarray:
        """Return data at specified row and column.

        Args:
            row (int): Table row.
            column (int): Table column.

        Returns:
            Numpy array element at [row, column]
        """
        return self.__array[row, column]

    def headerData(self, section: int, orientation,
                   role=QtCore.Qt.DisplayRole) -> QtCore.QVariant:
        """Numbers in the header, starting from zero.

        Args:
            section (int): Header section for which the data is requested.
            orientation (Qt orientation): Horizontal or vertical.
            role (Qt role): Default is DisplayRole.

        Returns:
            Header data, which is just the section number (QVariant).
        """
        if role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(section)
        return QtCore.QVariant()

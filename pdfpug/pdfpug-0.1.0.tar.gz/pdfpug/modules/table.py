#  MIT License
#
#  Copyright (C) 2019 Nekhelesh Ramananthan
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#  AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from typing import List, Union, Optional

from pdfpug.common import (
    BasePugElement,
    TableSpacing,
    TableRowStyle,
    TableRowType,
    TableType,
    Color,
)
from pdfpug.modules.row import Row


class Table(BasePugElement):
    """
    A Table lists data in organised manner making it easier to digest large amounts
    of data. It consists of :py:class:`~pdfpug.Row` and :py:class:`~pdfpug.Cell`.

    :param List header: Table header row
    :param List[List] data: Table body rows
    :param TableSpacing spacing: Table spacing (defaults to ``TableSpacing.comfortable``)
    :param Optional[TableRowStyle] striped: Table row style
    :param TableType table_type: Table type (defaults to ``TableType.celled``)
    :param Optional[Color] color: Table color

    A simple table consisting of just strings and numbers can be created as follows,

    >>> from pdfpug import Table
    >>> basic_table = Table(
    ...    header=['Serial Id', 'Fruit'],
    ...    data=[[1, 'Apple'], [2, 'Orange'], [3, 'Grape']]
    ... )

    A more advanced would looks something like the following,

    >>> from pdfpug import TableSpacing, TableRowStyle, State, Cell, Row, Color
    >>> advanced_table = Table (
    ...     header=['Hero', 'Role'],
    ...     data=[
    ...         ['Medusa', Cell('Carry', state=State.positive)],
    ...         Row(['Lion', 'Support'], state=State.active)
    ...     ],
    ...     striped=TableRowStyle.striped,
    ...     color=Color.green
    ... )
    """

    def __init__(
        self, header: Union[List, Row], data: List[Union[List, Row]], **kwargs
    ) -> None:
        super().__init__()

        # Data Variables
        self.header: Union[List, Row] = header
        self.data: List[Union[List, Row]] = data

        # Attributes
        self.spacing: TableSpacing = kwargs.get('spacing', TableSpacing.comfortable)
        self.striped: Optional[TableRowStyle] = kwargs.get('striped', None)
        self.table_type: TableType = kwargs.get('table_type', TableType.celled)
        self.color: Optional[Color] = kwargs.get('color', None)

    def _calculate_pug_str(self):
        # Gather attributes
        attributes = []
        for attribute in [self.spacing, self.striped, self.table_type, self.color]:
            if attribute:
                attributes.append(attribute.value)
        attributes.insert(0, 'ui')
        attributes.append('table')

        table_class = f'table(class="{" ".join(attributes)}")'
        header = self._construct_header()
        body = self._construct_body()

        self._pug_str = f'{table_class}\n{header}{body}'

    def _construct_header(self) -> str:
        header_pug = f'{(self.depth + 1) * self._tab}thead\n'
        if isinstance(self.header, Row):
            header_pug += self.header.pug
        else:
            header_pug += Row(self.header, row_type=TableRowType.header).pug

        return header_pug

    def _construct_body(self) -> str:
        body_pug = f'{(self.depth + 1) * self._tab}tbody\n'
        for row in self.data:
            if isinstance(row, Row):
                body_pug += row.pug
            else:
                body_pug += Row(row, row_type=TableRowType.body).pug

        return body_pug

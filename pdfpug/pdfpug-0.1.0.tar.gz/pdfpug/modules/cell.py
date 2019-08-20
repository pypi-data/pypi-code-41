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

from typing import Union, Optional

from pdfpug.common import BasePugElement, TableRowType, State, Alignment


class Cell(BasePugElement):
    """
    A Cell is the basic unit of a :py:class:`~pdfpug.Row`.

    :param Union[str, BasePugElement] data: Cell content
    :param TableRowType cell_type: Cell type (defaults to ``TableRowType.body``)
    :param Optional[int] row_span: Cell span across rows
    :param Optional[int] column_span: Cell span across columns
    :param Optional[State] state: Cell content state
    :param Optional[Alignment] alignment: Cell content horizontal alignment

    It can contain a simple string to complex elements like :py:class:`~pdfpug.Header`,
    :py:class:`~pdfpug.OrderedList` etc. This allows for embedding all kinds of data
    in a Cell.

    >>> from pdfpug import Cell, Header
    >>> header_cell = Cell(Header('Header Inside Cell'))

    A Cell has various customisation attributes that enable data to be represented
    accurately. For instance, if certain content need to be represented positively,
    one can do the following,

    >>> from pdfpug import State
    >>> pos_cell = Cell('Available', state=State.positive)
    """

    def __init__(self, data: Union[str, BasePugElement], **kwargs) -> None:
        super().__init__()

        # Data Variable
        self.data: Union[str, BasePugElement] = data

        # Attributes
        self.cell_type: TableRowType = kwargs.get('cell_type', TableRowType.body)
        self.row_span: Optional[int] = kwargs.get('row_span', 0)
        self.column_span: Optional[int] = kwargs.get('column_span', 0)
        self.state: Optional[State] = kwargs.get('state', None)
        self.alignment: Optional[Alignment] = kwargs.get('alignment', None)

    def _calculate_pug_str(self):
        self._pug_str = f'{self._construct_cell()} {self._construct_cell_content()}\n'

    def _construct_cell(self) -> str:
        # Gather attributes
        attributes = []
        for attribute in [self.state, self.alignment]:
            if attribute:
                attributes.append(attribute.value)

        cell_class = f'(class="{" ".join(attributes)}")' if attributes else ''
        row_span = f'(rowspan="{self.row_span}")' if self.row_span else ''
        column_span = f'(columnspan="{self.column_span}")' if self.column_span else ''

        return (
            f'{(self.depth + 3) * self._tab}{self.cell_type.value}'
            f'{cell_class}{row_span}{column_span}'
        )

    def _construct_cell_content(self) -> str:
        if isinstance(self.data, str):
            return self.data
        elif isinstance(self.data, BasePugElement):
            self.data.depth = self.depth + 4
            return f'\n{self.data.pug}'
        else:
            raise ValueError('Table cell is neither of type str nor BasePugElement')

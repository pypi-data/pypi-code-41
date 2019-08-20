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

__version__ = '0.1.0'

import os

from pdf_reports import write_report, pug_to_html

from pdfpug.common import (
    HeaderTier,
    Color,
    HeaderStyle,
    Alignment,
    ParagraphAlignment,
    State,
    TableType,
    TableRowStyle,
    TableSpacing,
    TableRowType,
)
from pdfpug.modules.header import Header
from pdfpug.modules.paragraph import Paragraph
from pdfpug.modules.orderedlist import OrderedList
from pdfpug.modules.unorderedlist import UnorderedList
from pdfpug.modules.table import Table
from pdfpug.modules.row import Row
from pdfpug.modules.cell import Cell


class PdfReport:
    def __init__(self):
        self._elements = []

    def add_element(self, element):
        self._elements.append(element)

    def generate_pdf(self, pdf_file_path: str) -> None:
        # TODO: Use a more temporary path to store the temporary pug file path
        pug_file_path = os.path.join(os.path.dirname(pdf_file_path), 'pug_file_new.pug')

        with open(pug_file_path, 'w') as pug_file_obj:
            for element in self._elements:
                pug_file_obj.write(element.pug + '\n')

        # Converting PUG to HTML
        html = pug_to_html(pug_file_path)
        print(html)

        # Converting HTML -> PDF
        write_report(html, pdf_file_path)

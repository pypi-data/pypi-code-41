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

__version__ = "0.2.0"

import tempfile
import warnings
from functools import lru_cache
from pathlib import Path
from typing import List

import jinja2
import weasyprint

from pdfpug.common import (
    BasePugElement,
    HeaderTier,
    Color,
    HeaderStyle,
    Alignment,
    ParagraphAlignment,
    State,
    SegmentType,
    SegmentEmphasis,
    SegmentSpacing,
    TableType,
    TableRowStyle,
    TableSpacing,
    TableRowType,
    ImageStyle,
    ImageLayout,
)
from pdfpug.modules.cell import Cell
from pdfpug.modules.header import Header
from pdfpug.modules.image import Image
from pdfpug.modules.images import Images
from pdfpug.modules.linebreak import LineBreak
from pdfpug.modules.orderedlist import OrderedList
from pdfpug.modules.pagebreak import PageBreak
from pdfpug.modules.paragraph import Paragraph
from pdfpug.modules.row import Row
from pdfpug.modules.segment import Segment
from pdfpug.modules.segments import Segments
from pdfpug.modules.table import Table
from pdfpug.modules.unorderedlist import UnorderedList


class PdfReport:
    """
    The main class that assembles all the elements together to create the PDF file.

    >>> from pdfpug import Header, PdfReport
    >>> header = Header('PdfPug Header')
    >>> report = PdfReport()
    >>> report.add_element(header)
    >>> report.generate_pdf('pug-report.pdf')
    """

    BASE_URL = Path(__file__).parent
    SEMANTIC_UI_CSS = BASE_URL / "css" / "semantic.min.css"
    STYLESHEET = BASE_URL / "css" / "style.css"

    def __init__(self):
        self._elements = []

    def add_element(self, element: BasePugElement) -> None:
        """
        Add an element to the PDF file

        :param element: Object instance of the different modules supported by PdfPug
        """
        if not isinstance(element, BasePugElement):
            raise TypeError
        self._elements.append(element)

    def add_elements(self, elements: List[BasePugElement]) -> None:
        """
        Add multiple elements in one call to the PDF file

        :param elements: Each element must be an object instance supported by PdfPug
        """
        for element in elements:
            if not isinstance(element, BasePugElement):
                raise TypeError
            self._elements.append(element)

    @lru_cache(maxsize=1)
    def _get_semantic_ui_css(self):
        with warnings.catch_warnings():
            css = weasyprint.CSS(filename=self.SEMANTIC_UI_CSS)
        return css

    @staticmethod
    def _convert_pug_to_html(pug_file_path: Path) -> str:
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                str(pug_file_path.parent) if pug_file_path.parent else "."
            ),
            extensions=["pypugjs.ext.jinja.PyPugJSExtension"],
        )

        template = jinja_environment.get_template(pug_file_path.name)

        return template.render()

    def _convert_html_to_pdf(self, html: str, pdf_file_path: str) -> None:
        html_obj = weasyprint.HTML(string=html)
        html_obj.write_pdf(
            pdf_file_path, stylesheets=[self._get_semantic_ui_css(), self.STYLESHEET]
        )

    def generate_pdf(self, pdf_file_path: str) -> None:
        """
        Generate PDF file

        :param pdf_file_path: Absolute path of the PDF file to be created
        """
        pug_file_path = tempfile.mktemp(suffix=".pug")
        with open(pug_file_path, "w+") as pug_file_obj:
            for element in self._elements:
                pug_file_obj.write(element.pug + "\n")

        html = self._convert_pug_to_html(Path(pug_file_path))

        self._convert_html_to_pdf(html, pdf_file_path)

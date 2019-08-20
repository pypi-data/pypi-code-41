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

from enum import Enum, unique


@unique
class HeaderTier(Enum):
    """
    Enum Weights to set the hierarchy of a header

    The weights are compatible with Markdown levels such as h1, h2, h3 etc.

    >>> from pdfpug import Header, HeaderTier
    >>> h1_header = Header('h1 Header', tier=HeaderTier.h1)
    >>> h2_header = Header('h2 Header', tier=HeaderTier.h2)
    >>> h3_header = Header('h3 Header', tier=HeaderTier.h3)

    .. figure:: ../_images/header_tiers.png
        :height: 150
    """

    #: Page level header. Equivalent to a markdown h1 header.
    h1 = 'h1'

    #: Section level header. Equivalent to a markdown h2 header.
    h2 = 'h2'

    #: Paragraph level header. Equivalent to a markdown h3 header.
    h3 = 'h3'


@unique
class HeaderStyle(Enum):
    """
    Enum header styles

    >>> from pdfpug import Header, HeaderStyle
    >>> block_header = Header('Block Header', style=HeaderStyle.block)
    """

    block = 'block'
    """
    The header is formatted to appear inside a content block
    
    .. figure:: ../_images/block_header.png
        :height: 50
    """

    dividing = 'dividing'
    """
    The header is formatted to divide itself from the content below it using a
    horizontal line

    .. figure:: ../_images/dividing_header.png
        :height: 35
    """


@unique
class Alignment(Enum):
    """
    Enum Alignment options
    """

    #: Right align content
    right = 'right aligned'

    #: Left align content
    left = 'left aligned'

    #: Justify content across the line
    justified = 'justified'

    #: Center align content
    center = 'center aligned'


@unique
class TableSpacing(Enum):
    """
    Enum Table row spacing
    """

    #: Tight spacing of row content
    tight = 'very compact'

    #: Compact spacing of row content
    compact = 'compact'

    #: Good spacing of row content
    comfortable = 'padded'

    #: Spacious padding of row content
    spacious = 'very padded'


@unique
class TableRowStyle(Enum):
    """
    Table row style
    """

    #: Set if alternate rows should be colored differently
    striped = 'striped'


@unique
class TableRowType(Enum):
    """
    Table row type
    """

    #: Header row
    header = 'th'

    #: Body row
    body = 'td'


@unique
class State(Enum):
    """
    Enum content state options
    """

    #: Positive content
    positive = 'positive'

    #: Negative content
    negative = 'negative'

    #: Error content
    error = 'error'

    #: Warning content
    warning = 'warning'

    #: Active content
    active = 'active'

    #: Disabled content
    disabled = 'disabled'


@unique
class TableType(Enum):
    celled = 'celled'
    simple = 'basic'
    bare = 'very basic'


@unique
class ParagraphAlignment(Enum):
    """
    Enum Alignment options
    """

    #: Left align content
    left = 'left'

    #: Right align content
    right = 'right'

    #: Center align content
    center = 'center'


@unique
class Size(Enum):
    """
    Enum Size options
    """

    #: Mini
    mini = 'mini'

    #: Tiny
    tiny = 'tiny'

    #: Small
    small = 'small'

    #: Large
    large = 'large'

    #: Huge
    huge = 'huge'

    #: Massive
    massive = 'massive'


@unique
class ListType(Enum):
    ordered = 'ordered'
    bulleted = 'bulleted'


@unique
class Orientation(Enum):
    """
    Enum Orientation options
    """

    #: Layout elements horizontally
    horizontal = 'horizontal'

    #: Layout elements vertically
    vertical = 'vertical'


@unique
class Color(Enum):
    red = 'red'
    orange = 'orange'
    yellow = 'yellow'
    olive = 'olive'
    green = 'green'
    teal = 'teal'
    blue = 'blue'
    purple = 'purple'
    violet = 'violet'
    pink = 'pink'
    brown = 'brown'
    grey = 'grey'

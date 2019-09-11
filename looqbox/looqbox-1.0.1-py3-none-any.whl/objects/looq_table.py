from looqbox.objects.looq_object import LooqObject
from looqbox.objects.table_head import TableHead
from looqbox.objects.table_body import TableBody
from looqbox.objects.table_footer import TableFooter
import json
import pandas as pd


class ObjTable(LooqObject):
    """
    Renders a PDF in the Looqbox's board using a PDF from the same directory of
    the response or from an external link (only works with HTTPS links).

    Attributes:
    --------
        :param pandas.DataFrame data: Table data content.
        :param str name: Table name, used as sheet name when an excel is generated from the table.
        :param str title: Table title.
        :param list head_group: Group the table headers.
        :param dict head_group_tooltip: Add a tooltip to a group of header.
        :param dict head_style: Add style to a table head.
        :param dict head_tooltip: Add a tooltip to a table head.
        :param dict value_format: Formats table data using the column as reference.
            Formats allowed: number:0, 1, 2..., percent:0, 1, 2, ..., date, dateTime.
        :param dict value_style: Table style (color, font, and other HTML's attributes) using the column as reference.
        :param dict value_tooltip: Add a tooltip with the information of the cell using the column as reference.
        :param dict value_link: Add link to table cell using the column as reference.
        :param list col_range: Limit the columns that the attributes will be displayed.
        :param dict row_style: Table style (color, font, and other HTML's attributes) using the row as reference.
            Obs: If the rowValueStyle has some element that is equal to the valueStyle,
            the function will prioritize the valueStyle element.
        :param dict row_format: Formats table data using the row as reference.
            Formats allowed: number:0, 1, 2..., percent:0, 1, 2, ..., date, dateTime.
        :param dict row_link: Add link to table cell using the row as reference.
        :param dict row_tooltip: Add a tooltip with the information of the cell using the row as reference
        :param list row_range: Limit the rows that the attributes will be displayed.
        :param dict or list total: Add a "total" as last row of the table.
        :param dict total_link: Add link to "total" row cell.
        :param dict total_style: Add style (color, font, and other HTML's attributes) to "total" row cell.
        :param dict total_tooltip: Add tooltip to "total" row cell.
        :param bool show_highlight: Enables or disables highlight on the table.
        :param int pagination_size: Number of rows per page on the table.
        :param bool searchable: Enables or disables a search box in the top left corner of the table.
        :param str search_string: Initial value inside the search box.
        :param bool show_border: Enables or disables table borders.
        :param bool show_head: Enables or disables table headers.
        :param bool show_option_bar: Enables or disables "chart and excel" option bar.
        :param bool sortable: Enables or disables a search box in the top left corner of the table.
        :param bool striped: Enables or disables colored stripes in rows.
        :param bool framed: Defines if the table will be framed.
        :param str framed_title: Add a title in the top of the table frame.
        :param bool stacked: Defines if the table will be stacked with other elements of the frame.
        :param list table_class: Table's class.

    Example:
    --------
        >>> table = ObjTable()
        #
        # Data
        >>> table.data = pandas.DataFrame({"Col1": range(1, 30), "Col2": range(1, 30)})
        #
        # Title
        >>> table.title = "test" # Or
        >>> table.title = ["test", "table"]
        #
        # Value Format
        ## "ColName" = "Format"
        >>> table.value_format = {"Col1": "number:2", "Col2": "percent:1"} # Or
        >>> table.value_format['Col1'] = "number:2"
        #
        # Row Format
        ## "RowNumber" = "Format"
        >>> table.row_format = {"1": "number:0"} # Or
        >>> table.row_format["2"] = "number:1"
        #
        # Value Link
        ## "ColName" = "NextResponseQuestion"
        >>> table.value_link = {"Col1": "test",
        ...                     "Col2": table.create_droplist({"text": "Head", "link": "Test of value {}"},
        ...                                                   [table.data["Col1"]])}
        #
        # Row Link
        ## "RowNumber" = paste(NextResponseQuestion)
        >>> table.value_link = {"1": "test", "2": "test2"}
        #
        # Value Style
        ## "ColName" = style
        >>> table.value_style = {"Col1": {"color": "blue", "background": "white"}}
        #
        # Row Style
        ## "RowNumber" = style
        >>> table.value_style = {"1": {"color": "blue", "background": "white"}}
        #
        # Value Tooltip
        >>> table.value_format = {"Col1": "tooltip", "Col2": "tooltip"}
        #
        # Row Tooltip
        >>> table.value_format = {"1": "tooltip", "2": "tooltip"}
        #
        # Total
        >>> table.total = [sum(table.data['Col1']), sum(table.data['Col2'])] # Or
        >>> table.total = {"Col1": sum(table.data['Col1']), "Col2": sum(table.data['Col2'])}
        #
        # Total Link
        >>> table.total_link = {"Col1": table.create_droplist({"text": "Head",
        ...                                                   "link": "Test of value " + str(table.total['Col1'])}),
        ...                     "Col2": "test2"}
        #
        # Total Style
        >>> table.total_style = {"Col1": {"color": "blue", "background": "white"},
        ...                      "Col2": {"color": "blue", "background": "white"}}
        #
        # Total Tooltip
        >>> table.total_style = {"Col1": "tooltip", "Col2": "tooltip"}
        #
        # Head Group
        >>> table.head_group = ["G1", "G1"]
        #
        # Head Group Tooltip
        >>> table.head_group_tooltip = {"G1": "This is the head of group G1"}
        #
        # Head Style
        >>> table.head_style = {"G1": {"color": "blue", "background": "white"}}
        #
        # Head Tooltip
        >>> table.tooltip = {"G1": "tooltip"}
        #
        # Logicals
        >>> table.stacked = True
        >>> table.show_head = False
        >>> table.show_border = True
        >>> table.show_option_bar = False
        >>> table.show_highlight = True
        >>> table.striped = False
        >>> table.sortable = True
        >>> table.searchable = False
        #
        # Search String
        >>> table.search_string = "search this"
        #
        # Atribute Column Range
        >>> table.col_range = [1, 5]
        >>> table.col_range = {"style": [0, 1], "format": [1, 2], "tooltip": [0, 2]}
        #
        # Pagination Size
        >>> table.pagination_size = 15

    Methods:
    --------
        create_droplist(text, link_values)
            :return: A list of the dicts mapped with the columns

    Properties:
    --------
        to_json_structure()
            :return: A JSON string.
    """
    def __init__(self, data=None, name="objTab", title=None, head_group=None, head_group_tooltip=None, head_style=None,
                 head_tooltip=None, value_format=None, value_style=None, value_tooltip=None, value_link=None,
                 col_range=None, row_style=None, row_format=None, row_link=None, row_tooltip=None, row_range=None,
                 total=None, total_link=None, total_style=None, total_tooltip=None, subtotal=None, subtotal_link=None,
                 subtotal_style=None, subtotal_tooltip=None, show_highlight=True, pagination_size=0, searchable=False,
                 search_string="", show_border=True, show_head=True, show_option_bar=True, sortable=True, striped=True,
                 framed=False, framed_title=None, stacked=True,
                 table_class=None):
        """
        Renders a PDF in the Looqbox's board using a PDF from the same directory of
        the response or from an external link (only works with HTTPS links).

        Attributes:
        --------
            :param pandas.DataFrame data: Table data content.
            :param str name: Table name, used as sheet name when an excel is generated from the table.
            :param str title: Table title.
            :param list head_group: Group the table headers.
            :param dict head_group_tooltip: Add a tooltip to a group of header.
            :param dict head_style: Add style to a table head.
            :param dict head_tooltip: Add a tooltip to a table head.
            :param dict value_format: Formats table data using the column as reference.
                Formats allowed: number:0, 1, 2..., percent:0, 1, 2, ..., date, dateTime.
            :param dict value_style: Table style (color, font, and other HTML's attributes) using the column as reference.
            :param dict value_tooltip: Add a tooltip with the information of the cell using the column as reference.
            :param dict value_link: Add link to table cell using the column as reference.
            :param list col_range: Limit the columns that the attributes will be displayed.
            :param dict row_style: Table style (color, font, and other HTML's attributes) using the row as reference.
                Obs: If the rowValueStyle has some element that is equal to the valueStyle,
                the function will prioritize the valueStyle element.
            :param dict row_format: Formats table data using the row as reference.
                Formats allowed: number:0, 1, 2..., percent:0, 1, 2, ..., date, dateTime.
            :param dict row_link: Add link to table cell using the row as reference.
            :param dict row_tooltip: Add a tooltip with the information of the cell using the row as reference
            :param list row_range: Limit the rows that the attributes will be displayed.
            :param dict or list total: Add a "total" as last row of the table.
            :param dict total_link: Add link to "total" row cell.
            :param dict total_style: Add style (color, font, and other HTML's attributes) to "total" row cell.
            :param dict total_tooltip: Add tooltip to "total" row cell.
            :param bool show_highlight: Enables or disables highlight on the table.
            :param int pagination_size: Number of rows per page on the table.
            :param bool searchable: Enables or disables a search box in the top left corner of the table.
            :param str search_string: Initial value inside the search box.
            :param bool show_border: Enables or disables table borders.
            :param bool show_head: Enables or disables table headers.
            :param bool show_option_bar: Enables or disables "chart and excel" option bar.
            :param bool sortable: Enables or disables a search box in the top left corner of the table.
            :param bool striped: Enables or disables colored stripes in rows.
            :param bool framed: Defines if the table will be framed.
            :param str framed_title: Add a title in the top of the table frame.
            :param bool stacked: Defines if the table will be stacked with other elements of the frame.
            :param list table_class: Table's class.

        Example:
        --------
            >>> table = ObjTable()
            #
            # Data
            >>> table.data = pandas.DataFrame({"Col1": range(1, 30), "Col2": range(1, 30)})
            #
            # Title
            >>> table.title = "test" # Or
            >>> table.title = ["test", "table"]
            #
            # Value Format
            ## "ColName" = "Format"
            >>> table.value_format = {"Col1": "number:2", "Col2": "percent:1"} # Or
            >>> table.value_format['Col1'] = "number:2"
            #
            # Row Format
            ## "RowNumber" = "Format"
            >>> table.row_format = {"1": "number:0"} # Or
            >>> table.row_format["2"] = "number:1"
            #
            # Value Link
            ## "ColName" = "NextResponseQuestion"
            >>> table.value_link = {"Col1": "test",
            ...                     "Col2": table.create_droplist({"text": "Head", "link": "Test of value {}"},
            ...                                                   [table.data["Col1"]])}
            #
            # Row Link
            ## "RowNumber" = paste(NextResponseQuestion)
            >>> table.value_link = {"1": "test", "2": "test2"}
            #
            # Value Style
            ## "ColName" = style
            >>> table.value_style = {"Col1": {"color": "blue", "background": "white"}}
            #
            # Row Style
            ## "RowNumber" = style
            >>> table.value_style = {"1": {"color": "blue", "background": "white"}}
            #
            # Value Tooltip
            >>> table.value_format = {"Col1": "tooltip", "Col2": "tooltip"}
            #
            # Row Tooltip
            >>> table.value_format = {"1": "tooltip", "2": "tooltip"}
            #
            # Total
            >>> table.total = [sum(table.data['Col1']), sum(table.data['Col2'])] # Or
            >>> table.total = {"Col1": sum(table.data['Col1']), "Col2": sum(table.data['Col2'])}
            #
            # Total Link
            >>> table.total_link = {"Col1": table.create_droplist({"text": "Head",
            ...                                                   "link": "Test of value " + str(table.total['Col1'])}),
            ...                     "Col2": "test2"}
            #
            # Total Style
            >>> table.total_style = {"Col1": {"color": "blue", "background": "white"},
            ...                      "Col2": {"color": "blue", "background": "white"}}
            #
            # Total Tooltip
            >>> table.total_style = {"Col1": "tooltip", "Col2": "tooltip"}
            #
            # Head Group
            >>> table.head_group = ["G1", "G1"]
            #
            # Head Group Tooltip
            >>> table.head_group_tooltip = {"G1": "This is the head of group G1"}
            #
            # Head Style
            >>> table.head_style = {"G1": {"color": "blue", "background": "white"}}
            #
            # Head Tooltip
            >>> table.tooltip = {"G1": "tooltip"}
            #
            # Logicals
            >>> table.stacked = True
            >>> table.show_head = False
            >>> table.show_border = True
            >>> table.show_option_bar = False
            >>> table.show_highlight = True
            >>> table.striped = False
            >>> table.sortable = True
            >>> table.searchable = False
            #
            # Search String
            >>> table.search_string = "search this"
            #
            # Atribute Column Range
            >>> table.col_range = [1, 5]
            >>> table.col_range = {"style": [0, 1], "format": [1, 2], "tooltip": [0, 2]}
            #
            # Pagination Size
            >>> table.pagination_size = 15
        """
        super().__init__()
        if table_class is None:
            table_class = []
        if framed_title is None:
            framed_title = {}
        if subtotal is None:
            subtotal = []
        self.data = data
        self.name = name
        self.title = title
        self.head_style = head_style
        self.head_tooltip = head_tooltip
        self.head_group = head_group
        self.head_group_tooltip = head_group_tooltip
        self.show_head = show_head
        self.head_style = head_style
        self.head_tooltip = head_tooltip
        self.head_group = head_group
        self.head_group_tooltip = head_group_tooltip
        self.value_format = value_format
        self.value_style = value_style
        self.value_tooltip = value_tooltip
        self.value_link = value_link
        self.col_range = col_range
        self.row_style = row_style
        self.row_format = row_format
        self.row_link = row_link
        self.row_range = row_range
        self.row_tooltip = row_tooltip
        self.total = total
        self.total_link = total_link
        self.total_style = total_style
        self.total_tooltip = total_tooltip
        self.subtotal = subtotal
        self.subtotal_link = subtotal_link
        self.subtotal_style = subtotal_style
        self.subtotal_tooltip = subtotal_tooltip
        self.stacked = stacked
        self.show_border = show_border
        self.show_head = show_head
        self.show_highlight = show_highlight
        self.show_option_bar = show_option_bar
        self.search_string = search_string
        self.searchable = searchable
        self.pagination_size = pagination_size
        self.sortable = sortable
        self.striped = striped
        self.framed = framed
        self.framed_title = framed_title
        self.table_class = table_class

    @staticmethod
    def create_droplist(text, link_values=None):
        """
        Create a droplist from a list of values and a base text.

        The function map all the values of the columns with a format in the text using {} as base.

        Example:
        --------
            x = create_droplist({"text": Header, "link": "Link text {} and text2 {}"}, [df[col1], df[col2]])

            The first {} will use the value from df[col1] and the second {} will use the value from df[col2]

            If the user wants more than one droplist it pass a list of this function
            x = [
                create_droplist({"text": Header, "link": "Link text {} and text2 {}"}, [df[col1], df[col2]])
                create_droplist({"text": Header2, "link": "Link text {} and text2 {}"}, [df[col1], df[col2]])
            ]

        :param text: Is the base text of the droplist, use the default dict {"text": Header, "link": "Link text"}
        Example: {"text": Header, "link": "Link text {} and text2 {}"}

        :param link_values: A list with the columns to map the values in the text

        :return: A list of the dicts mapped with the columns
        """
        link_list = []
        format_values = []
        lists_length = 0

        if link_values is None:
            return text

        if not isinstance(link_values, list):
            link_values = [link_values]

        for i in range(len(link_values)):
            # Transforming all pandas Series types in a common list
            if isinstance(link_values[i], pd.Series):
                link_values[i] = list(link_values[i])
            # If is only a value transform to list
            elif not isinstance(link_values[i], list):
                link_values[i] = [link_values[i]]

            # Get lists length
            if lists_length == 0:
                lists_length = len(link_values[i])
            elif len(link_values[i]) != lists_length:
                raise Exception("List " + str(i) + " in droplist values has different length from others")

        for value_i in range(lists_length):
            for list_i in range(len(link_values)):
                format_values.append(link_values[list_i][value_i])
            text_base = text.copy()
            text_base["link"] = text_base["link"].format(*format_values)
            link_list.append(text_base)
            format_values = []

        return link_list

    @property
    def to_json_structure(self):
        """
        Creates the JSON structure to be read by the FES.

        :return: A JSON string.
        """
        table_head = TableHead(self.data, self.head_style, self.head_tooltip, self.head_group, self.head_group_tooltip,
                               self.show_head)
        table_body = TableBody(self.data, self.value_format, self.value_style, self.value_tooltip, self.value_link,
                               self.col_range, self.row_style, self.row_format, self.row_link, self.row_tooltip,
                               self.row_range)
        table_footer = TableFooter(self.data, self.total, self.total_link, self.total_style, self.total_tooltip,
                                   self.subtotal, self.subtotal_link, self.subtotal_style, self.subtotal_tooltip,
                                   self.value_format)

        head_json = table_head.to_json_structure
        body_json = table_body.to_json_structure
        footer_json = table_footer.to_json_structure

        if not isinstance(self.title, list):
            self.title = [self.title]

        json_content = {'objectType': "table",
                        'title': self.title,
                        'header': head_json,
                        'body': body_json,
                        'footer': footer_json,
                        'searchable': self.searchable,
                        'searchString': self.search_string,
                        'paginationSize': self.pagination_size,
                        'framed': self.framed,
                        'framedTitle': self.framed_title,
                        'stacked': self.stacked,
                        'showBorder': self.show_border,
                        'showOptionBar': self.show_option_bar,
                        'showHighlight': self.show_highlight,
                        'striped': self.striped,
                        'sortable': self.sortable,
                        "class": self.table_class
                        }

        # Transforming in JSON
        table_json = json.dumps(json_content, indent=1, allow_nan=False)

        return table_json

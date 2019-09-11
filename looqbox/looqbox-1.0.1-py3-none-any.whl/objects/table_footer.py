from looqbox.objects.looq_object import LooqObject
import pandas as pd
from collections import defaultdict, OrderedDict
from looqbox.objects.table_cell import TableCell
import types


class TableFooter(LooqObject):

    def __init__(self, table_data=None, total=None, total_link=None, total_style=None, total_tooltip=None,
                 subtotal=None, subtotal_link=None, subtotal_style=None, subtotal_tooltip=None, value_format=None):
        super().__init__()
        self.table_data = table_data
        self.total = total
        self.total_link = total_link
        self.total_style = total_style
        self.total_tooltip = total_tooltip
        self.subtotal = subtotal
        self.subtotal_link = subtotal_link
        self.subtotal_style = subtotal_style
        self.subtotal_tooltip = subtotal_tooltip
        self.value_format = value_format

    @staticmethod
    def _get_total_attributes(col_name, col_attribute):
        element_attribute = None

        if col_attribute is not None and col_name in col_attribute.keys():
            # If function call the function with the col_name
            if isinstance(col_attribute, types.FunctionType):
                element_attribute = col_attribute(col_name)
            else:
                element_attribute = col_attribute[col_name]

        return element_attribute

    @staticmethod
    def _get_subtotal_attributes(col_name, col_attribute, subtotal_index):
        element_attribute = None

        if isinstance(col_attribute, list):
            col_attribute = col_attribute[subtotal_index]

        if col_attribute is not None and col_name in col_attribute.keys():
            # If function call the function with the col_name
            if isinstance(col_attribute, types.FunctionType):
                element_attribute = col_attribute(col_name)
            else:
                element_attribute = col_attribute[col_name]

        return element_attribute

    @staticmethod
    def _transform_droplist(data_drop):
        """
             Create the droplists for the table elements

             :return List of dictionaries with keys text and link
             """

        link_list = []

        # If its a single dict it will be transformed into a list of dicts, however if its a str it will raise Exception
        if isinstance(data_drop, str):
            raise Exception("Links with only strings must not be in a list")

        if not isinstance(data_drop[0], list):
            data_drop = [data_drop]

        for i in range(len(data_drop[0])):
            link_list_element = []

            for j in range(len(data_drop)):
                if 'text' not in data_drop[j][i]:
                    raise Exception("Text missing in droplist link")
                elif 'link' not in data_drop[j][i]:
                    raise Exception("Link missing in droplist link")

                text = data_drop[j][i]['text']
                link = data_drop[j][i]['link']

                link_list_element.append({"text": text, "link": link})

            link_list.append(link_list_element)

        if not len(link_list) > 1:
            link_list = link_list[0]

        return link_list

        # link_list = []
        #
        # if not isinstance(data_drop, list):
        #     data_drop = [data_drop]
        #
        # for col in data_drop:
        #     if 'text' in col.keys() and len(col['text'].strip()) > 0:
        #         text = col['text']
        #
        #         if 'link' in col.keys() and len(col['link'].strip()) > 0:
        #             link = col['link']
        #             link_list.append({"text": text, "link": link})
        #
        # return link_list

    @staticmethod
    def _format_to_class(value_format):

        value_format = value_format.split(":")

        s = value_format[0].strip()

        return "lq" + s[0:1].upper() + s[1:]

    @staticmethod
    def _get_total_value(element, value):
        if isinstance(value, LooqObject):
            element.cell_value = value.to_json_structure
        else:
            element.cell_value = value

    @staticmethod
    def _get_subtotal_value(element, value):
        if isinstance(value, LooqObject):
            element.cell_value = value.to_json_structure
        else:
            element.cell_value = value

    @staticmethod
    def _get_total_style(col_name, element, value, value_style):
        if value_style is not None:
            if isinstance(value_style, types.FunctionType):
                element.cell_style = value_style(value)

            elif isinstance(value_style, pd.DataFrame):
                element.cell_style = value_style[col_name]

            else:
                element.cell_style = value_style

    @staticmethod
    def _get_subtotal_style(col_name, element, value, value_style):
        if value_style is not None:
            if isinstance(value_style, types.FunctionType):
                element.cell_style = value_style(value)

            elif isinstance(value_style, pd.DataFrame):
                element.cell_style = value_style[col_name]

            else:
                element.cell_style = value_style

    def _get_total_link(self, element, value, value_link):
        if value_link is not None:
            if isinstance(value_link, types.FunctionType):
                element.cell_link = value_link(value)

            elif isinstance(value_link, dict) or isinstance(value_link, list):
                # If the dict will contain a key droplist, the key link should not exist
                element.cell_droplist = self._transform_droplist(value_link)

            elif isinstance(value_link, str):
                element.cell_link = value_link

            else:
                raise Exception("Formato de link não permitido")

    def _get_subtotal_link(self, element, value, value_link):
        if value_link is not None:
            if isinstance(value_link, types.FunctionType):
                element.cell_link = value_link(value)

            elif isinstance(value_link, dict) or isinstance(value_link, list):
                # If the dict will contain a key droplist, the key link should not exist
                element.cell_droplist = self._transform_droplist(value_link)

            elif isinstance(value_link, str):
                element.cell_link = value_link

            else:
                raise Exception("Formato de link não permitido")

    def _get_total_format(self, element, value, value_format, col_name):
        if value_format is not None:
            if isinstance(value_format, types.FunctionType):
                element.cell_format = value_format(value)
                element.cell_class = self._format_to_class(value_format)

            elif isinstance(value_format, pd.DataFrame):
                element.cell_format = value_format[col_name]
                element.cell_class = self._format_to_class(value_format[col_name])

            else:
                element.cell_format = value_format
                element.cell_class = self._format_to_class(value_format)

    def _get_subtotal_format(self, element, value, value_format, col_name):
        if value_format is not None:
            if isinstance(value_format, types.FunctionType):
                element.cell_format = value_format(value)
                element.cell_class = self._format_to_class(value_format)

            elif isinstance(value_format, pd.DataFrame):
                element.cell_format = value_format[col_name]
                element.cell_class = self._format_to_class(value_format[col_name])

            else:
                element.cell_format = value_format
                element.cell_class = self._format_to_class(value_format)

    @staticmethod
    def _get_total_tooltip(element, value_tooltip):
        if value_tooltip is not None:
            if len(value_tooltip.strip()) != 0:
                element.cell_tooltip = value_tooltip

    @staticmethod
    def _get_subtotal_tooltip(element, value_tooltip):
        if value_tooltip is not None:
            if len(value_tooltip.strip()) != 0:
                element.cell_tooltip = value_tooltip

    def _get_footer_subtotal(self, table_data, table_subtotal, subtotal_index):
        subtotal_dict = OrderedDict()
        if isinstance(table_subtotal, list):

            if len(table_subtotal) != len(table_data.keys()):
                raise Exception('"Total" size is different from the number of columns. To use total this way, '
                                'please use a dictionary.')

            table_total_index = 0
            for key in table_data.keys():
                subtotal_dict[key] = table_subtotal[table_total_index]
                table_total_index += 1

        elif isinstance(table_subtotal, dict):
            table_total_index = 0
            for key in table_data.keys():
                if key in table_subtotal.keys():
                    subtotal_dict[key] = table_subtotal[key]
                else:
                    subtotal_dict[key] = "-"
                table_total_index += 1

        for col_name in subtotal_dict:

            # Get columns attributes
            value_style = self._get_subtotal_attributes(col_name, self.subtotal_style, subtotal_index)
            value_link = self._get_subtotal_attributes(col_name, self.subtotal_link, subtotal_index)
            value_format = self._get_subtotal_attributes(col_name, self.value_format, subtotal_index)

            value_tooltip = None
            if self.subtotal_tooltip is not None and col_name in self.subtotal_tooltip.keys():
                if isinstance(self.subtotal_tooltip, dict):
                    value_tooltip = self.subtotal_tooltip[col_name]
                else:
                    value_tooltip = self.subtotal_tooltip

            # Initializing a dict with keys: None
            element = TableCell()

            value = subtotal_dict[col_name]

            # Add value to the dict
            self._get_subtotal_value(element, value)

            # Add style to the dict
            self._get_subtotal_style(col_name, element, value, value_style)

            # Add link to the dict
            self._get_subtotal_link(element, value, value_link)

            # Add tooltip to the dict
            self._get_subtotal_tooltip(element, value_tooltip)

            # Add format to the dict
            self._get_subtotal_format(element, value, value_format, col_name)

            # Add the element dict to the value cell
            # self.remove_json_nones(element)

            subtotal_dict[col_name] = element

        return subtotal_dict

    def _get_footer_total(self, table_data, table_total):
        total_dict = OrderedDict()
        if isinstance(table_total, list):

            if len(table_total) != len(table_data.keys()):
                raise Exception('"Total" size is different from the number of columns. To use total this way, '
                                'please use a dictionary.')

            table_total_index = 0
            for key in table_data.keys():
                total_dict[key] = table_total[table_total_index]
                table_total_index += 1

        elif isinstance(table_total, dict):
            table_total_index = 0
            for key in table_data.keys():
                if key in table_total.keys():
                    total_dict[key] = table_total[key]
                else:
                    total_dict[key] = "-"
                table_total_index += 1

        for col_name in total_dict:

            # Get columns attributes
            value_style = self._get_total_attributes(col_name, self.total_style)
            value_link = self._get_total_attributes(col_name, self.total_link)
            value_format = self._get_total_attributes(col_name, self.value_format)

            value_tooltip = None
            if self.total_tooltip is not None and col_name in self.total_tooltip.keys():
                if isinstance(self.total_tooltip, dict):
                    value_tooltip = self.total_tooltip[col_name]
                else:
                    value_tooltip = self.total_tooltip

            # Initializing a dict with keys: None
            element = TableCell()

            value = total_dict[col_name]

            # Add vgialue to the dict
            self._get_total_value(element, value)

            # Add style to the dict
            self._get_total_style(col_name, element, value, value_style)

            # Add link to the dict
            self._get_total_link(element, value, value_link)

            # Add tooltip to the dict
            self._get_total_tooltip(element, value_tooltip)

            # Add format to the dict
            self._get_total_format(element, value, value_format, col_name)

            # Add the element dict to the value cell
            total_dict[col_name] = element

        return total_dict

    @property
    def to_json_structure(self):

        table_total = self.total
        table_subtotal = self.subtotal
        table_data = self.table_data

        if not isinstance(table_subtotal, list):
            raise Exception("Table subtotal must be a list of dictionaries")

        if isinstance(self.table_data, pd.DataFrame):
            table_data = table_data.to_dict(into=OrderedDict, orient='dict')

        # Build total
        table_total = self._get_footer_total(table_data, table_total)

        total_list = []
        for col in table_total.keys():
            total_list.append(table_total[col].to_json_structure)

        # Build subtotal
        subtotal_index = 0
        subtotal_main_list = []
        for subtotal in table_subtotal:
            subtotal_list = []
            subtotal = self._get_footer_subtotal(table_data, subtotal, subtotal_index)
            for col in subtotal.keys():
                subtotal_list.append(subtotal[col].to_json_structure)
            subtotal_main_list.append(subtotal_list)
            subtotal_index += 1

            # Create general json
        footer_json = {"content": total_list, "subtotal": subtotal_main_list}

        return footer_json

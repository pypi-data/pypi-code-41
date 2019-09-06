import re
from lxml import etree  # pylint: disable=E0401


__copyright__ = 'Copyright (C) 2019, Nokia'


class RstTableCreator():
    """
    Based on the principles of xml, creates table in rst format.
    Creates table in rst format basing on xml tables
    """

    # Is used to eliminate pipes-spaces and pipe at the end of a line
    pipe_regex = re.compile(r'\| |\|$')

    def change_robot_table_to_rst_table(self, file_path):
        """Summary line.

        Opens file with xml, searches doc nodes,
        changes Robot XML tables to rst tables and
        saves it as the same xml.

        Args:
            file_path (str): File path to the Robot XML tables

        Returns:
            Nothing

        """
        root = etree.parse(file_path)
        for i in root.iter('doc'):
            i.text = self._change_table_to_rst_table(i.text)

        with open(file_path, 'wb') as f:
            f.write(etree.tostring(root))

    def _change_table_to_rst_table(self, txt):
        """Summary line.

        Changes given text table to rst format

        Args:
            txt (str): Text to be changed

        Returns
            result_txt (str): Text in rst format

        """
        table_content = []
        result_txt = ''
        txt = txt.split('\n')

        for line in txt:
            if line and line[0] == '|' and line[-1] == '|':
                table_content.append(self._make_row(line))
            else:
                if table_content:
                    result_txt += self._tabulate(table_content)
                    table_content = []
                if line and (line[0] == '|' or line[-1] == '-'):
                    result_txt += '\n\n' + line[2:]
                else:
                    result_txt += '\n' + line
        if table_content:
            result_txt += self._tabulate(table_content)

        return result_txt + '\n'

    def _make_row(self, line_content):
        """Summary line.

        Takes text line and makes row for table

        Args:
            line_content (str): One line of text

        Returns:
            List representing one row of table

        """
        splitted_line = self.pipe_regex.split(line_content)
        line_content = [x.strip() for x in splitted_line[1:-1]]
        return line_content

    def _tabulate(self, table):
        """Summary line.

        Makes table in rst format

        Args:
            table (list(list(str))): Table to be converted

        Returns:
            Table converted to rst format

        """
        max_lengths = self._column_elem_max_lengths(table)
        border = self._make_border(max_lengths)
        text = '\n\n' + border

        for row in table:
            for index, elem in enumerate(row):
                text += elem.ljust(max_lengths[index] + 2)
            text = text[:-2] + '\n'

        return text + border + '\n'

    def _column_elem_max_lengths(self, table):
        """Summary line.

        Takes list of lists e.g [['aa','bb','cc'],['a','bbb','cc'], ['a','b','cccc']],
        Returns a tuple containing the length of the longest element in every column
        Example above would return: (2, 3, 4)

        Args:
            table (list(list(str))): Table from which lengths are to be obtained

        Returns:
            tuple(int)

        """
        table = self._prepare_list(table)
        max_lengths = []
        for column in range(len(table[0])):
            elem_lengths = []
            for row in range(len(table)):  # pylint: disable=C0200
                column_elem_len = len(table[row][column])
                elem_lengths.append(column_elem_len)
            column_max_len = max(elem_lengths)
            max_lengths.append(column_max_len)

        return tuple(max_lengths)

    @staticmethod
    def _prepare_list(row_list):
        """Line summary.

        Checks which elem is the longest
        Makes every elem has the same length like max

        Args:
            row_list (list(list(str))): The table

        Returns:
            tuple(list(str)): Padded lists

        """
        max_length = len(max(row_list, key=len))
        for row in row_list:
            padd_amount = max_length - len(row)
            row += [' '] * padd_amount

        return tuple(row_list)

    @staticmethod
    def _make_border(max_lengths):
        """Line summary.

        Makes string of correct border.
        Method iterates max_lengths tuple and
        adds to return string enough '='

        Args:
            max_lengths (tuple(int)): Lengths of the longest element in each column of
            the table

        Returns:
            string: Border string

        """
        border = '\n'
        space_len = 2
        for length in max_lengths:
            border += '=' * length + ' ' * space_len
        return border[:-2] + '\n'

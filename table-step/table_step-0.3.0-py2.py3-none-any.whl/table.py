# -*- coding: utf-8 -*-

"""Non-graphical part of the Table step in SEAMM"""

import logging
import seamm
from seamm_util import ureg, Q_, units_class  # noqa: F401
import numpy as np
import os.path
import pandas
import table_step

logger = logging.getLogger(__name__)
methods = [
    'create',
    'read',
    'save',
    'print',
    'print current row',
    'append row',
    'next row',
    'add columns',
    'set element',
    'get element'
]  # yapf: disable


class Table(seamm.Node):

    def __init__(self, flowchart=None, extension=None):
        """Setup the non-graphical part of the Table step in SEAMM.

        Keyword arguments:
        """
        logger.debug('Creating Table {}'.format(self))

        # What are we doing?
        self._method = 'create'

        # Information about the table
        self.name = 'table1'
        self.filename = ''
        self.index_column = 'default'

        # Used for editing and adding columns
        self.tmp_columns = []

        # For getting and setting individual values
        self.column_index = ''
        self.row_index = ''
        self.value = ''
        self.variable_name = ''

        # Initialize our parent class
        super().__init__(
            flowchart=flowchart, title='Table', extension=extension
        )

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        if value in table_step.methods:
            self._method = value
        else:
            raise RuntimeError(
                'The table method must one of ' +
                ', '.join(table_step.methods) + 'not "' + value + '"'
            )

    def run(self):
        """Do what we need for the table, as dictated by the 'method'
        """

        tablename = self.get_value(self.name)

        if self.method == 'create':
            table = pandas.DataFrame()
            defaults = {}
            for d in self.tmp_columns:
                column_name = self.get_value(d['name'])
                if column_name not in table.columns:
                    if d['type'] == 'boolean':
                        if d['default'] == '':
                            default = False
                        else:
                            default = bool(d['default'])
                    elif d['type'] == 'integer':
                        if d['default'] == '':
                            default = 0
                        else:
                            default = int(d['default'])
                    elif d['type'] == 'float':
                        if d['default'] == '':
                            default = np.nan
                        else:
                            default = float(d['default'])
                    elif d['type'] == 'string':
                        default = d['default']

                    table[column_name] = default
                    defaults[column_name] = default
            if self.index_column != 'default':
                index_column = self.get_value(self.index_column)
                try:
                    index_column = table.columns[int(index_column)]
                except ValueError:
                    if index_column not in table.columns:
                        raise RuntimeError(
                            "Table create: column '{}'".format(index_column) +
                            ' for index does not exist'
                        )
                table.set_index(
                    index_column, inplace=True, verify_integrity=True
                )

            logger.info("Creating table '{}'".format(tablename))
            self.set_variable(
                tablename, {
                    'type': 'pandas',
                    'table': table,
                    'defaults': defaults,
                }
            )
        elif self.method == 'read':
            filename = self.get_value(self.filename)

            logger.debug('  read table from {}'.format(filename))

            table = pandas.read_csv(filename)

            if self.index_column != 'default':
                index_column = self.get_value(self.index_column)
                try:
                    index_column = table.columns[int(index_column)]
                except ValueError:
                    if index_column not in table.columns:
                        raise RuntimeError(
                            "Table create: column '{}'".format(index_column) +
                            ' for index does not exist'
                        )
                table.set_index(
                    index_column, inplace=True, verify_integrity=True
                )

            logger.debug('  setting up dict in {}'.format(tablename))
            self.set_variable(
                tablename, {
                    'type': 'pandas',
                    'filename': filename,
                    'format': 'csv',
                    'table': table,
                    'defaults': {}
                }
            )

            logger.info('Succesfully read table from {}'.format(filename))
        elif self.method == 'save':
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            if 'filename' not in table_handle:
                table_handle['filename'] = os.path.join(
                    self.flowchart.root_directory, tablename + '.csv'
                )
                # raise RuntimeError(
                #     "Table save: table '{}' has no associated filename"
                #     .format(tablename)
                # )
            filename = table_handle['filename']

            if 'format' in table_handle:
                file_format = table_handle['format']
            else:
                file_format = 'csv'

            if file_format == 'csv':
                table_handle['table'].to_csv(filename)
            elif file_format == 'json':
                table_handle['table'].to_json(filename)
            elif file_format == 'json':
                with open(filename, 'w') as fd:
                    fd.write(table_handle['table'].to_json())
            elif file_format == 'excel':
                table_handle['table'].to_excel(filename)
            else:
                raise RuntimeError(
                    "Table save: cannot handle format '" + file_format +
                    "' for file '" + filename
                )
        elif self.method == 'print':
            table_handle = self.get_variable(tablename)
            table = table_handle['table']
            print('\n{}'.format(tablename))
            with pandas.option_context(
                    'display.max_rows', None,
                    'display.max_columns', None,
                    'display.width', None,
            ):  # yapf: disable
                print(table)

        elif self.method == 'print current row':
            table_handle = self.get_variable(tablename)
            table = table_handle['table']
            index = table_handle['current index']
            index = table.index.get_loc(index)
            lines = table.to_string(header=True).splitlines()

            # print('index = {}'.format(index))
            # print(lines)
            # print('-----')

            if index == 0:
                print('\n{}'.format(tablename))
                print('\n'.join(lines[0:3]))
            else:
                print(lines[index + 1])

        elif self.method == 'append row':
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            if 'defaults' in table_handle:
                defaults = table_handle['defaults']
            else:
                defaults = {}
            table = table_handle['table']
            column_types = {}
            for column_name, column_type in zip(table.columns, table.dtypes):
                if column_type == 'object':
                    column_types[column_name] = 'string'
                elif column_type == 'bool':
                    column_types[column_name] = 'boolean'
                elif column_type == 'int64':
                    column_types[column_name] = 'integer'
                elif column_type == 'float64':
                    column_types[column_name] = 'float'

            new_row = {}

            for d in self.tmp_columns:
                column_name = self.get_value(d['name'])
                value = self.get_value(d['value'])
                column_type = column_types[column_name]
                if value == 'default':
                    if column_name in defaults:
                        value = defaults[column_name]
                    else:
                        if column_type == 'boolean':
                            value = False
                        elif column_type == 'integer':
                            value = 0
                        elif column_type == 'float':
                            value = np.nan
                        elif column_type == 'string':
                            value = ''
                new_row[column_name] = value

            table = table.append(new_row, ignore_index=True)
            seamm.flowchart_variables[tablename]['table'] = table
            seamm.flowchart_variables[tablename]['current index'] = (
                table.shape[0] - 1
            )
        elif self.method == 'next row':
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            table_handle['current index'] += 1

        elif self.method == 'add columns':
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table save: table '{}' does not exist.".format(tablename)
                )
            table_handle = self.get_variable(tablename)
            table = table_handle['table']
            for d in self.tmp_columns:
                column_name = self.get_value(d['name'])
                if column_name in table.columns:
                    # Need to check if this is an error
                    pass
                else:
                    if d['type'] == 'boolean':
                        if d['default'] == '':
                            default = False
                        else:
                            default = bool(d['default'])
                    elif d['type'] == 'integer':
                        if d['default'] == '':
                            default = 0
                        else:
                            default = int(d['default'])
                    elif d['type'] == 'float':
                        if d['default'] == '':
                            default = np.nan
                        else:
                            default = float(d['default'])
                    elif d['type'] == 'string':
                        default = d['default']
                    table[d['name']] = default
        elif self.method == 'get element':
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table get element: table '{}' does not exist."
                    .format(tablename)
                )
            if self.column_index is None:
                raise RuntimeError(
                    "Table get element: the column index must be given"
                )
            if self.row_index is None:
                raise RuntimeError(
                    "Table get element: the row index must be given"
                )
            if self.variable_name is None:
                raise RuntimeError(
                    "Table get element: the name of the variable to "
                    "set to the value must be given"
                )

            table_handle = self.get_variable(tablename)
            table = table_handle['table']

            variable_name = self.get_value(self.variable_name)
            column_index = self.get_value(self.column_index)
            row_index = self.get_value(self.row_index)

            value = table.at[row_index, column_index]
            self.set_variable(variable_name, value)
        elif self.method == 'set element':
            if not self.variable_exists(tablename):
                raise RuntimeError(
                    "Table get element: table '{}' does not exist."
                    .format(tablename)
                )
            if self.column_index is None:
                raise RuntimeError(
                    "Table get element: the column index must be given"
                )
            if self.row_index is None:
                raise RuntimeError(
                    "Table get element: the row index must be given"
                )
            if self.value is None:
                raise RuntimeError(
                    "Table get element: the name of the variable to "
                    "set to the value must be given"
                )

            table_handle = self.get_variable(tablename)
            table = table_handle['table']

            value = self.get_value(self.value)
            column_index = self.get_value(self.column_index)
            row_index = self.get_value(self.row_index)

            table.at[row_index, column_index] = value
        else:
            raise RuntimeError(
                'The table method must be one of ' +
                ', '.join(table_step.methods) + 'not "' + self.method + '"'
            )

        return super().run()

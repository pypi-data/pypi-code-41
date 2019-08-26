import os

from flexp import utils
import logging


class CsvFile(object):

    def __init__(self, filename, column_names, overwrite=False):
        """CSV File that updates trial-by-trial

        Args:
            filename:
                name of the file. If the file doesn't exist, it is created,
                if the file exists, new records are just appended to the end.
                Note that this may result in corrupted csv files if you change
                your column names half way through data collection
            column_names:
                names of columns in the csv file. This is used to create a
                header on new files and it is used to validate records that you
                append to the file
            overwrite:
                If this is set to true, existing files will be overwritten and
                new records will not be added at the end.
        """
        self.filename = filename
        if os.path.exists(self.filename) and overwrite is False:
            logging.info('Appending data to file {}'.format(self.filename))
        else:
            utils.write_line(','.join(column_names) + '\n', self.filename, 'w')
        self.column_names = column_names

    def add_record(self, data):
        """Add a record to the data file

        Args:
            data:
                A dictionary with one key per column.

        Raises:
            ValueError:
                if the dictionary keys don't match the columns of the file
        """
        if not self._validate_columns(data):
            raise ValueError('Invalid column names')
        formatted_data = [str(data[column]) for column in self.column_names]
        utils.write_line(','.join(formatted_data) + '\n', self.filename, 'a')

    def _validate_columns(self, data):
        if not set(data.keys()) == set(self.column_names):
            logging.error('Keys in data but not in csv file:',
                          set(data.keys()) - set(self.column_names))
            logging.error('Keys in csv file but not in data:',
                          set(self.column_names) - set(data.keys()))
            return False
        return True

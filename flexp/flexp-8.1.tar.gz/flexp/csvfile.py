import os

from flexp import utils
import logging


class CsvFile(object):

    def __init__(self, filename, column_names, overwrite=False):
        self.filename = filename
        if os.path.exists(self.filename) and overwrite is False:
            logging.info('Appending data to file {}'.format(self.filename))
        else:
            utils.write_line(','.join(column_names) + '\n', self.filename, 'w')
        self.column_names = column_names

    def add_record(self, data):
        if not self.validate_columns(data):
            raise ValueError('Invalid column names')
        formatted_data = [str(data[column]) for column in self.column_names]
        utils.write_line(','.join(formatted_data) + '\n', self.filename, 'a')

    def validate_columns(self, data):
        if not set(data.keys()) == set(self.column_names):
            logging.error('Keys in data but not in csv file:',
                          set(data.keys()) - set(self.column_names))
            logging.error('Keys in csv file but not in data:',
                          set(self.column_names) - set(data.keys()))
            return False
        return True

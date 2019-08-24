"""
This helperclass reads TWISS files in TFS format produced by MADX.
See more information in twissreader.py.

TODO:
    - SPLIT ON spaces in header does not work (see test script ORIGIN var)
    - DOCSTRINGS with parameters
"""
__author__ = "Christian Staufenbiel"
__date__ = "05/07/2019"
__version__ = "0.1"

import pandas as pd
import shlex


class TwissReaderTFS():
    """ Stores the header and data of a TWISS file. """

    def __init__(self, filename):
        # Open file
        s = self.__readfile(filename)
        self.header, self.data = self.__split_header_data(s)

    def __readfile(self, filename):
        """ Reads content of a file """
        # Check if file is a csv file
        if filename.split('.')[1] != 'tfs':
            raise NotImplementedError('TwissReader: Currently only tfs files are implemented!')
        f = None
        try:
            f = open(filename, 'r')
        except FileNotFoundError:
            print('TwissReader: The file {} was not found!'.format(filename))
            raise
        # Read strng from file and return
        res = f.read()
        f.close()
        return res

    def __split_header_data(self, s):
        """ Splits string of TFS file to header and data. """

        # Split lines
        lines = s.split('\n')

        # Find index of data description / end of header
        data_desc_idx = 0
        for i, line in enumerate(lines):
            if len(line) > 0 and line[0] == '*':
                data_desc_idx = i
        if not data_desc_idx:
            raise RuntimeError('TwissReaderTFS: Couldnt find data description line!')

        # Take all header lines and store in the header dictionary
        header = {}
        for line in lines[0:data_desc_idx]:
            if len(line) == 0 or line[0] != '@':
                continue
            # Split at all spaces
            line = shlex.split(line)
            # Remove all empty strings from line list
            line = list(filter(lambda x: x != '', line))
            # Get key and value from the line
            key = line[1]
            val = line[-1].replace('"', '')
            # Try to convert to float if possible
            try:
                val = float(val)
            except:
                pass
            # Add key/val-pair to header
            header[key] = val

        # Get all column names for the dataframe
        line = lines[data_desc_idx]
        # delete star from the data description line
        line = line[1:]
        line = line.split(' ')
        # Delete all empty strings from list -> column names
        columns = list(filter(lambda x: x != '', line))
        # Run trough all data lines and add data to array
        data = []
        for line in lines[data_desc_idx+2:]:
            # Continue on empty lines
            if len(line) == 0:
                continue
            # Remove all " amd split on spaces
            line = line.replace('"', '')
            line = line.split(' ')
            # Delete empty string elements from list
            line = list(filter(lambda x: x != '', line))
            # Try to convert to float
            for i, val in enumerate(line):
                try:
                    line[i] = float(val)
                except:
                    pass
            # append to data
            data.append(line)

        # Create dataframe
        data = pd.DataFrame(data, columns=columns)
        data = data.set_index(columns[0])
        return header, data


if __name__ == '__main__':
    # TODO: Write a test
    print('Running example of twissreader_tfs.py')
    tw = TwissReaderTFS('test.tfs')
    print('Header: ')
    print(tw.header)
    print('Data:')
    print(tw.data.head(5))
    # Access data
    print(tw.data.loc['DRIFT_1', 'BETX'])

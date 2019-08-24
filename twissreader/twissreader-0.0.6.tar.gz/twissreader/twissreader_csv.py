"""
This helperclass reads TWISS files in CSV format produced by MADX.
See more information in twissreader.py.

TODO:
    - DOCSTRINGS with parameters
"""
__author__ = "Christian Staufenbiel"
__date__ = "05/07/2019"
__version__ = "0.1"

import numpy as np
import pandas as pd
import sys


class TwissReaderCSV():
    """ Stores the header and data of a TWISS file."""

    # Initialize
    def __init__(self, filename):
        # Class variables
        self.header = {}
        self.data = pd.DataFrame([])
        # Open file
        s = self.__readfile(filename)
        split = self.__split_header_data_footer(s)

    def __readfile(self, filename):
        """ Reads content of a file """
        # Check if file is a csv file
        if filename.split('.')[1] != 'csv':
            raise NotImplementedError('TwissReader: Currently only csv files are implemented!')
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

    def __split_header_data_footer(self, s, sep=','):
        """
        Splits string of a Twiss file to header, data and footer.
        We assume that that the header has always 2 entries (var_name, value)
        and the data has more than 2 entries.
        """
        # Split on line break
        split = s.split('\n')
        # Get the number of entries (noe) per line
        noe_list = []
        for l in split:
            noe = len(l.split(sep))
            noe_list.append(noe)
        noe_list = np.array(noe_list)
        # Check if there is only header, data and footer
        # Note: The line before the data, containing descriptions has one column
        #       less than the data lines, since data lines end with a comma
        if np.unique(noe_list).shape[0] > 4:
            raise RuntimeError('TwissReader: More than 3 sections in file! ')

        # Get the unique number of elements per line, sorted by occurrence
        unique, index = np.unique(noe_list, return_index=True)
        unique = unique[index.argsort()]

        # Get indices where noe per line are the same
        idx_set = [np.argwhere(noe_list == x) for x in unique]
        header_idx = idx_set[0].flatten()  # Indices of header
        descr_data_idx = idx_set[1].flatten()  # Indices of variable description
        data_idx = idx_set[2].flatten()  # Indices of data
        footer_idx = idx_set[3].flatten()  # Indices of footer

        # Create header dictionary
        self.header = self.__create_dictionary(split, header_idx, sep=sep)

        # Create pandas dataframe
        self.data = self.__create_dataframe(split, descr_data_idx, data_idx, sep=sep)

        # TODO: Handle footer (but I think there is no such thing)
        return split

    def __create_dictionary(self, split, idx, sep=','):
        """ Creates a dictionary from the split values and given indices """
        dict = {}
        # Iterate through all indices corresponding to the dictionary
        for i in idx:
            # Split into variable name and value
            l = split[i].split(sep)
            # Raise error if there is more than name and value
            if len(l) > 2:
                raise RuntimeError('TwissReader: Can not form dict!')
            key, val = l
            # Remove the " characters from the names and variables
            key = key.replace('"', '')
            val = val.replace('"', '')
            # Try to convert value to float
            try:
                val = float(val)
            except:
                pass
            # Add key/val to dictionary
            dict[key] = val

        return dict

    def __create_dataframe(self, split, descr_idx, data_idx, sep=','):
        """ Creates a dataframe given idx for description and data and the split"""
        # Retrieve column names
        if len(descr_idx) > 1:
            raise RuntimeError('Too many indices for description!')
        col_names = split[descr_idx[0]].replace('"', '')
        col_names = col_names.split(sep)

        # Retrieve data
        data = []
        for i in data_idx:
            l = split[i].replace('"', '')
            # Remove ending comma (TODO: CLEANER WAY)
            l = l[:-2]
            # Split line and convert to float if possible
            vals = l.split(sep)
            for i, val in enumerate(vals):
                val = val.replace(' ', '')  # remove whitespaces
                try:
                    vals[i] = float(val)
                except:
                    continue
            # Append to data array
            data.append(vals)

        # Create DataFrame and return
        df = pd.DataFrame(data, columns=col_names)
        df = df.set_index(col_names[0])
        return df


if __name__ == '__main__':
    # TODO: WRITE SMALL TEST
    print('Running example of twissreader_csv.py')
    # Read a Twiss CSV file
    tw = TwissReaderCSV('test.csv')
    # Print Header
    print('Header:')
    print(tw.header)
    # Print data head
    print('Data:')
    print(tw.data.head(5))
    # Access the BETA function at one element
    print(tw.data.loc['DRIFT_1', 'BETX'])

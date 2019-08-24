"""
This helperclass reads TWISS files format produced by MADX.
The header is returned as a dictionary and the data array
as a pandas dataframe.

There are some TODOS spread over the code, but here a small list:
    - Add TFS support
    - DOCSTRINGS with parameters
    - Search function for elements and variables (indices and columns)
"""
__author__ = "Christian Staufenbiel"
__date__ = "05/07/2019"
__version__ = "0.1"

import numpy as np
import pandas as pd
from .twissreader_csv import TwissReaderCSV
from .twissreader_tfs import TwissReaderTFS


class TwissReader():
    """ Stores the header and data of a TWISS file."""

    def __init__(self, filename):
        """ Initializing the object"""
        # class variables
        self.header = {}
        self.data = pd.DataFrame([])
        # Check the ending
        filetype = filename.split('.')[1]
        if filetype == 'csv':
            tw = TwissReaderCSV(filename)
        elif filetype == 'tfs':
            tw = TwissReaderTFS(filename)
        else:
            raise NotImplementedError('TwissReader: Filetype {} not recognized.'.format(filetype))

        # Copy data and header to this object
        self.data = tw.data
        self.header = tw.header

    def __getitem__(self,key):
        """ Indexing the objects reads from the Dataframe """
        # If there are several keys (tuple) it's probably meant to go in the dataframe
        if isinstance(key,tuple):
            return self.data.loc[key]
        try:
            return self.data[key]
        except:
            pass
        try:
            return self.header[key]
        except:
            sys.exit('Could not find the key in the TwissFile!')


    def find_element(self, search_string):
        """ Searches MADX elements containing the search_string """
        res = []
        for elem in self.data.index:
            if search_string in elem:
                res.append(elem)
        return res

    def find_variable(self, search_string):
        """ Searches for variables containing the search_string """
        res = []
        for var in self.data.columns:
            if search_string in var:
                res.append(var)
        return res


if __name__ == '__main__':
    print('running twissreader.py')

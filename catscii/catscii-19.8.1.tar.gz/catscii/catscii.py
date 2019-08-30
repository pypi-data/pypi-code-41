'''
This file contains the code to 
open the catalogs passed by the user.

Each catalog that is open becomes a python 
object with attributes.

Author: R. THOMAS
Place: ESO
Year: GPL v3.0
'''


###python imports
import numpy

###metadata
__version__ = 1.3
__author__ = 'R. THOMAS'
__licence__ = 'GPLv3'
__credits__ = "Romain Thomas"
__maintainer__ = "Romain Thomas"
__website__ = 'https://github.com/astrom-tom/catscii'
__email__ = "the.spartan.proj@gmail.com"
__status__ = "released"
__year__ = '2018-19'


class load_cat(object):
    '''
    This class creates, from an ascii catalog,
    a python object
    '''

    def __init__(self, catalog, header):
        '''
        Class constructor

        Parameters
        ----------
        catalog : str
                  this is the catalog (eventually with its path) you want to open

        header  : Boolean
                  True if the catalog contains a header, otherwise false

        Attributes
        ----------
        name    : str
                  Name of the catalog, as passed by the user

        cat     : numpy array
                  numpy array loaded from the catalog (all columns are string by default)

        header  : list of string
                  identification of each column. If no header is present in the catalog
                  then each column are renames col1, col2, ....colN

        Note
        ----
        For the header of the catalog to be recognized, it must start by an hash (#)
        and provide a name for EVERY column Ex:
        #X     Y   Xerrp   Xerrm   Yerrp   Yerrm
        1       1   0.5     0.2     0.3     0.1
        2       2   0.3     0.2     0.1     0.4
        3      3   0.1     0.05    0.1     0.4
        4      4   0.1     0.07    0.8     0.2
        5      5   0.2     0.3     0.15    0.23
        6      6   0.1     0.4     0.6     0.1
        7      7   0.2     0.3     0.4     0.1
        '''
       
        ###the name of the catalog becomes an attribute
        self.name = catalog

        if header:
            self.__get_header()
        else:
            self.__fake_header()

    def __fake_header(self):
        '''
        In case there is no header in the catalog we create a fake one
        Attributes
        ----------
        Ncolumn  : int
              number of column from the catalog

        header: list
                list of column names

        Nrows:  int
                number of rows
        '''

        ####extract number of column
        self.cat = numpy.genfromtxt(self.name, dtype='str').T
        self.Ncolumn = len(self.cat)  ###--> number of column
        self.Nrows = len(self.cat.T)

        ##create fake header
        self.header = []
        for i in range(self.Ncolumn):
            self.header.append('Col%s'%(i+1))

        
    def __get_header(self):
        '''
        This method take the catalog
        and extract the header
        
        Attributes
        ----------
        Nc  : int
              number of column from the catalog

        header: list
                list of column names

        Nrows:  int
                number of rows
        '''
        ####extract number of column
        self.cat = numpy.genfromtxt(self.name, dtype='str').T
        self.Ncolumn = len(self.cat)  ###--> number of column
        self.Nrows = len(self.cat.T)
        

        ####read the first line of the raw file
        with open(self.name, 'r') as F:
            firstLine = F.readline()

        hashtag = firstLine[0]

        ###we check if the header start with the hash, if not we raise the error
        if hashtag != '#':
            raise header_hash('No hash at the beginning of the header')
        else:
            firstLine = firstLine[1:-1] 

        ##split the header:
        N_header = len(firstLine.split())
            
        ###if the number of header detected is different from the number of column..error
        if N_header != self.Ncolumn:
            raise header_length('The number of headers is different from the number of columns')
        else:
            self.header = firstLine.split()


    def get_column(self, name, datatype=None):
        '''
        This method extracts the column given by the name in the parameter
        from the loaded catalog.

        Parameters
        ----------
        name
                str,  name of the column to extract

        datatype
                str, optionnal, give the datatype of the column

        return
        ------
        column
                numpy array, 1D numpy array of the column that 
                             was extracted.
        '''
        
        if name not in self.header:
            raise missing_in_header('%s not in catalog header'%name)

        else:
            #find the index of the column in the catalog
            index = numpy.where(numpy.array(self.header) == name)

            column = self.cat[index][0]

            ###convert to type given
            if datatype != None:
                column = column.astype(datatype)

            return column

    def get_line(self, column, line, datatype='None'):
        '''
        This method extract the line given in parameters

        Parameters
        ----------
        column
                string, column where to look at for line identification

        line
                string, in the given column, we will extract the line(s) where the value is


        Return
        ------
        extracted_line
                        list of dictionnary
                        each dictionnary correspond to a line where the column given
                        by the user is equal to the line value that was passed.
                        The keywords of each dictionnary are the names of the column and the values
                        are the values at the requested line
        '''

        if column not in self.header:
            raise missing_in_header('%s not in catalog header'%name)

        ##extract column
        col = self.get_column(column)


        ##and look for the line where column = line
        index = numpy.where(col == line)

        ##and extract line
        Line = []
        for i in self.cat.T[index]:
            indiv_line = {}
            for j in range(len(self.header)):
                indiv_line[self.header[j]] = i[j]
            Line.append(indiv_line)

        #if len(Line) < 1:
        #    Line = Line[0]

        return Line

class header_hash(Exception):
    def __init__(self, value):
        self.error = value

class header_length(Exception):
    def __init__(self, value):
        self.error = value

class missing_in_header(Exception):
    def __init__(self, value):
        self.error = value


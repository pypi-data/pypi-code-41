# -*- coding: utf-8 -*-
'''
    geophpy.filesmanaging.grd
    -------------------------

    SurferGrid grid files input and output management.

    :copyright: Copyright 2018-2019 Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

import numpy as np
import struct

#------------------------------------------------------------------------------#
# Classes to managed grids from Surfer (Golden Software)                       #
#------------------------------------------------------------------------------#
# List of the treated grid file format
gridtype_list = ['surfer7bin', 'surfer6bin', 'surfer6ascii']
gridformat_list = ['Surfer 7 binary Grid', 'Surfer 6 binary Grid', 'Surfer 6 ascii Grid']

class GridError(Exception):
    pass


class SurferGrid:
    ''' Class to manage Golden Software Surfer grid. '''

    def __init__(self, nRow=None, nCol=None, xLL=None, yLL=None, xSize=None,
                 ySize=None, zMin=None, zMax=None, data=None, BlankValue=1.71041e38, Rotation=0, filename=None):
        self.nRow = nRow
        self.nCol = nCol
        self.xLL = xLL
        self.yLL = yLL
        self.xSize = xSize
        self.ySize = ySize
        self.zMin = zMin
        self.zMax = zMax
        self.Rotation = Rotation
        self.BlankValue = BlankValue
        self.data = data
        self.filename = filename

    def read(self, filename=None, gridtype=None):
        '''
        Read data from Golden Software Surfer grid formats.

        wrapper of the fromfile() method.

        '''

        if filename is not None:
            self.filename = filename

        if gridtype is not None:
            self.gridtype = gridtype

        return self.fromfile(self.filename, gridtype=self.gridtype)

    @staticmethod
    def fromfile(filename, gridtype=None):
        '''
        Read data from Golden Software Surfer grid files.

        Parameters
        ----------
        filename : str
            Name of the grid file to read.

        gridtype : str {'surfer7bin', 'surfer6bin', 'surfer6ascii', None}, optional
            Format of the grid file to read. 
            If None, it will be determined from the file itself.

        Returns
        -------
        SurferGrid instance

        '''

        return GRDReader(filename=filename, gridtype=gridtype).read()

    def write(self, filename=None, gridtype=None):
        '''
        Write data to Golden Software Surfer grid file.

        wrapper of the tofile() method.

        '''

        if filename is not None:
            self.filename = filename

        if gridtype is not None:
            self.gridtype = gridtype

        return self.tofile(self, self.filename, gridtype=self.gridtype)

    @staticmethod
    def tofile(grid, filename, gridtype='surfer7bin'):
        '''
        Writes data to Golden Software Surfer grid file.

        Parameters
        ----------
        filename : str
            Name of the grid file to write

        gridtype : str {'surfer7bin', 'surfer6bin', 'surfer6ascii'}, optional
            Format of the grid file to write. By default 'surfer7bin'

        '''

        return GRDWriter(filename=filename, gridtype=gridtype, grid=grid).write()

    def getXmin(self):
        ''' Return grid minimum x value. '''
        return  self.xLL

    def getXmax(self):
        ''' Return grid maximum x value. '''
        return  self.xSize*(self.nCol-1) + self.xLL

    def getYmin(self):
        ''' Return grid minimum x value. '''
        return  self.yLL

    def getYmax(self):
        ''' Return grid maximum y value. '''
        return  self.ySize*(self.nRow-1) + self.yLL

    def getZmin(self):
        ''' Return grid mùinimum Z value. '''
        return  self.zMin

    def getZmax(self):
        ''' Return grid maximum Z value. '''
        return  self.zMax

    def NanToBlank(self, BlankValue=None):
        ''' Convert nans in the data to grid blank values. '''

        if BlankValue is not None:
            self.BlankValue = BlankValue

        self.data[np.isnan(self.data)] = self.BlankValue

        return  self

    def BlankToNan(self, BlankValue=None):
        ''' Convert grid blank values in the data to nans. '''

        if BlankValue is not None:
            self.BlankValue = BlankValue

        self.data[self.data==self.BlankValue] = np.nan

        return self

    def plot(self, cmap=None, vmin=None, vmax=None):
        ''' Basic plot of the Surfer Grid '''

        if self.data is not None:
            import matplotlib.pyplot as plt
            import matplotlib.colors as colors

            fig = plt.figure()
            ax = fig.add_subplot(111)
            norm = colors.Normalize()

            xmin = self.xLL
            xmax = self.xLL + (self.nCol-1)*self.xSize
            ymin = self.yLL
            ymax = self.yLL + (self.nRow-1)*self.ySize
            
            extent = (xmin, xmax, ymin, ymax)
            data = self.data

            im = ax.imshow(data, extent=extent, interpolation=None,
                           cmap=cmap, vmin=vmin, vmax=vmax, norm=norm,
                           origin='lower', aspect='auto')

            if self.filename is not None:
                title = self.filename
                fig.canvas.set_window_title(title)
                

            fig.show()

            return fig


class GRDReader:
    '''
    Class to read Golden Software Surfer grid formats.

    Reads data from Surfer 7 binary grid, Surfer 6 binary grid
    and Surfer 6 ascii grid files.

    Based on steno3d_surfer/parser

    '''

    def __init__(self, filename=None, gridtype=None):
        ''' Instantiate a Surfer grid reader. '''
        self.filename = filename
        self.gridtype = gridtype

    @classmethod
    def surfer7bin(cls, filename=None):
        ''' Instantiate a Surfer 7 binary grid reader. '''

        return cls(filename=filename, gridtype='surfer7bin')

    @classmethod
    def surfer6bin(cls, filename=None):
        ''' Instantiate a Surfer 6 binary grid reader. '''

        return cls(filename=filename, gridtype='surfer6bin')

    @classmethod
    def surfer6ascii(cls, filename=None):
        ''' Instantiate a Surfer 6 ascii grid reader. '''

        return cls(filename=filename, gridtype='surfer6ascii')

    def read(self, filename=None, gridtype=None):
        '''
        Read data from Golden Software Surfer grid formats.

        Parameters
        ----------
        filename : str
            Name of the grid file to read.

        gridtype : str {'surfer7bin', 'surfer6bin', 'surfer6ascii', None}, optional
            Format of the grid file to read. 
            If None, it will be determined from the file itself.

        Returns
        -------
        SurferGrid instance

        '''

        # Check filename
        if filename is not None:
            self.filename = filename

        # Invalid filename
        if self.filename is None:

            raise ValueError('Invalid or no filename provided')

            return SurferGrid()
            
        # Using given grid reader
        if gridtype in ['surfer7bin', 'surfer6bin', 'surfer6ascii']:
            reader = self._select_reader_from_gridtype(gridtype)

        # Selecting appropriate grid reader
        else:
            if gridtype is not None:
                raise ValueError('Invalid gridtype provided')

            reader = self._select_reader_from_file()

        # reafing grid file
        try:
            surfer_grid = reader(self.filename)

        except Exception as e:
            print(e)

            surfer_grid =  SurferGrid()

        return surfer_grid

    def _select_reader_from_gridtype(self, gridtype):
        ''' Select the appropriate grid reader from given gridtype. '''

        valid_gridtype_reader = {
            'surfer7bin' : self._read_surfer7bin,
            'surfer6bin' : self._read_surfer6bin,
            'surfer6ascii': self._read_surfer6ascii
            }

        return valid_gridtype_reader[gridtype]

    def _select_reader_from_file(self):
        ''' Select the appropriate grid reader from the grd file. '''

        file = open(self.filename, 'rb')
        tagID = struct.unpack('4s', file.read(4))[0]
        file.close()

        # Surfer 7 binary grid tag
        if tagID == b'DSRB':
            reader = self._read_surfer7bin
            self.gridtype = 'surfer7bin'

        # Surfer 6 binary grid tag
        elif tagID == b'DSBB':
            reader = self._read_surfer6bin
            self.gridtype = 'surfer6bin'

        # Surfer 6 ascii grid tag
        elif tagID == b'DSAA':
            reader = self._read_surfer6ascii
            self.gridtype = 'surfer6ascii'

        # Unkwnow tag
        else:
            self.gridtype = None
            raise GridError(('Invalid file identifier for Surfer .grd file. '
                             'Must be DSRB, DSBB, or DSAA'))

        return reader

    def _read_surfer7bin(self, filename):
        ''' Read Golden Software Surfer 7 binary grid formats. '''

        with open(filename, "rb") as file:

            # Headers section
            # Valid surfer 7 binary grid file
            tagID = struct.unpack('4s', file.read(4))[0]
            if  tagID != b'DSRB':
                raise GridError(('Invalid surfer 7 binary grid file'
                                 'First 4 characters must be DSRB')
                                 )

            # Passing headers
            HeaderSize = struct.unpack('<i',file.read(4))[0]  # Size of Header section
            Version = struct.unpack('<i',file.read(4))[0]  # Header Section Version
                                                           # 1: then any value >= BlankValue will be blanked.
                                                           # 2: then any value == BlankValue will be blanked.

            # Grid section
            tagID = struct.unpack('4s', file.read(4))[0]
            if tagID != b'GRID':
                raise GridError(('Invalid Surfer 7 binary grid file '
                                 'GRID section expected directly after '
                                 'the HEADERS section but %s encountered') %(tagID)
                                 )

            # Length in bytes of the grid section
            Nbytes = struct.unpack('<i', file.read(4))[0]
            if Nbytes != 72:
                raise GridError(('Invalid Surfer 7 binary grid file '
                                 'Expected length in bytes of the grid section '
                                 'is 72 but %d encountered.') % (Nbytes)
                                  )

            # Grid info
            nRow = struct.unpack('<i', file.read(4))[0]  # int
            nCol = struct.unpack('<i', file.read(4))[0]  # int
            xLL = struct.unpack('<d', file.read(8))[0]  # double
            yLL = struct.unpack('<d', file.read(8))[0]  # double
            xSize = struct.unpack('<d', file.read(8))[0]  # double
            ySize = struct.unpack('<d', file.read(8))[0]  # double
            zMin = struct.unpack('<d', file.read(8))[0]  # double
            zMax = struct.unpack('<d', file.read(8))[0]  # double
            Rotation = struct.unpack('<d', file.read(8))[0]  # double
            BlankValue = struct.unpack('<d', file.read(8))[0]  # double

            # Data section
            tagID = struct.unpack('4s', file.read(4))[0]  # str
            if tagID != b'DATA':
                raise GridError(('Invalid Surfer 7 binary grid file '
                                 'DATA section expected directly after '
                                 'the GRID section but %s encountered.') %(tagID)
                                 )

            datalen = struct.unpack('<i', file.read(4))[0] #  Length in bytes of the data section

            if datalen != nCol*nRow*8:
                raise GridError(('Invalid Surfer 7 binary grid file '
                                 'Inconsistency between expected DATA '
                                 'Length and nRow, nCol. '
                                 'Expected length is (%d) but %s encountered.') %(nCol*nRow*8, datalen)
                                 )

            # Data
            data = np.empty((nRow, nCol))

            for row in range(nRow):  # Y
                for col in range(nCol): # X
                    data[row][col] = struct.unpack('<d', file.read(8))[0] # float

            data[data >= BlankValue] = np.nan

            grid = SurferGrid(nRow=nRow, nCol=nCol, xLL=xLL, yLL=yLL,
                              xSize=xSize, ySize=ySize, zMin=zMin, zMax=zMax,
                              data=data, BlankValue=BlankValue, filename=filename)

            return grid

    def _read_surfer6bin(self, filename):
        ''' Read Golden Software Surfer 6 binary grid formats. '''

        with open(filename, "rb") as file:

            # Valid surfer 6 binary grid file
            tagID = struct.unpack('4s', file.read(4))[0]
            if  tagID != b'DSBB':
                raise GridError(('Invalid surfer 6 binary grid file'
                                 'First 4 characters must be DSBB')
                                )

            # Grid info 
            nCol = struct.unpack('<h', file.read(2))[0]  # short
            nRow = struct.unpack('<h', file.read(2))[0]  # short
            xMin = struct.unpack('<d', file.read(8))[0]  # double
            xMax = struct.unpack('<d', file.read(8))[0]  # double
            yMin = struct.unpack('<d', file.read(8))[0]  # double
            yMax = struct.unpack('<d', file.read(8))[0]  # double
            zMin = struct.unpack('<d', file.read(8))[0]  # double
            zMax = struct.unpack('<d', file.read(8))[0]  # double

            xSize = (xMax-xMin)/(nCol-1)
            ySize = (yMax-yMin)/(nRow-1)
            xLL = xMin
            yLL = yMin

            BlankValue = 1.701410009187828e+38

            # Data
            data = np.empty((nRow, nCol))

            for row in range(nRow):  # Y
                for col in range(nCol): # X
                    data[row][col] = struct.unpack('<f', file.read(4))[0] # float

            data[data >= BlankValue] = np.nan

            grid = SurferGrid(nRow=nRow, nCol=nCol, xLL=xLL, yLL=yLL,
                              xSize=xSize, ySize=ySize, zMin=zMin, zMax=zMax,
                              data=data, BlankValue=BlankValue, filename=filename)

            return grid

    def _read_surfer6ascii(self, filename):
        ''' Read Golden Software Surfer 6 ascii grid formats. '''

        with open(filename, "r") as file:

            # Valid surfer 6 binary grid file
            tagID = file.readline().strip()
            if  tagID != 'DSAA':
                raise GridError('Invalid surfer 6 ascii grid file '
                                'First 4 characters must be DSAA'
                                  )
            # Grid info
            nCol, nRow = [int(n) for n in file.readline().split()]
            xMin, xMax = [float(n) for n in file.readline().split()]
            yMin, yMax = [float(n) for n in file.readline().split()]
            zMin, zMax = [float(n) for n in file.readline().split()]
            
            xSize = (xMax-xMin)/(nCol-1)
            ySize = (yMax-yMin)/(nRow-1)
            xLL = xMin
            yLL = yMin

            BlankValue = 1.70141e38

            # Data
            data = np.empty((nRow, nCol))

            for i in range(nRow):
                data[i, :] = [float(n) for n in file.readline().split()]

            data[np.where(data >= BlankValue)] = np.nan

            grid = SurferGrid(nRow=nRow, nCol=nCol, xLL=xLL, yLL=yLL,
                              xSize=xSize, ySize=ySize, zMin=zMin, zMax=zMax,
                              data=data, BlankValue=BlankValue, filename=filename)

            return grid

class GRDWriter:
    '''
    Class to write Golden Software Surfer grid formats.

    Writes data to Surfer 7 binary grid, Surfer 6 binary grid
    and Surfer 6 ascii grid files.

    '''

    def __init__(self, filename=None, gridtype='surfer7bin', grid=None):
        ''' Instantiate a Surfer grid writer. '''
        self.filename = filename
        self.gridtype = gridtype
        self.grid = grid

    @classmethod
    def surfer7bin(cls, filename=None, grid=None):
        ''' Instantiate a Surfer 7 binary grid writer. '''

        return cls(filename=filename, gridtype='surfer7bin')

    @classmethod
    def surfer6bin(cls, filename=None, grid=None):
        ''' Instantiate a Surfer 6 binary grid writer. '''

        return cls(filename=filename, gridtype='surfer6bin')

    @classmethod
    def surfer6ascii(cls, filename=None, grid=None):
        ''' Instantiate a Surfer 6 ascii grid writer. '''

        return cls(filename=filename, gridtype='surfer6ascii')

    def write(self, filename=None, gridtype=None, grid=None):
        '''
        Writes data to Golden Software Surfer grid file.

        Parameters
        ----------
        filename : str
            Name of the grid file to write

        gridtype : str {'surfer7bin', 'surfer6bin', 'surfer6ascii'}, optional
            Format of the grid file to write. By default 'surfer7bin'.

        grid : SurferGrid object
            Surfer grid to write.

        '''

        # Check filename
        if filename is not None:
            self.filename = filename

        # Invalid filename
        if self.filename is None:

            raise ValueError('Invalid or no filename provided')

        # Invalid surfer grid
        if grid is not None:
            self.grid = grid

        if self.grid.__class__ != SurferGrid().__class__:
            raise ValueError(('Invalid or no SurferGrid object provided. '
                             'Expected type is %s, encoutered is %s.') %(SurferGrid().__class__, self.grid.__class__)
                             )

        # Check gridtype
        if gridtype is not None:
            self.gridtype = gridtype
    
        if  self.gridtype not in ['surfer7bin', 'surfer6bin', 'surfer6ascii']:
            raise ValueError(('Invalid Surfer grid format. '
                             'gridtype must be "surfer7bin", "surfer6bin" or "surfer6ascii" '
                              'but %s encourtered') %(self.gridtype)
                             )

        # Using given writer to write grid file
        writer = self._select_writer_from_gridtype(self.gridtype)
        try:
            writer(self.filename, self.grid)

        except Exception as e:
            print(e)

    def _select_writer_from_gridtype(self, gridtype):
        ''' Select the appropriate grid writer from given gridtype. '''

        valid_gridtype_writer = {
            'surfer7bin' : self._write_surfer7bin,
            'surfer6bin' : self._write_surfer6bin,
            'surfer6ascii': self._write_surfer6ascii
            }

        return valid_gridtype_writer[gridtype]

    def _write_surfer7bin(self, filename, grid, version=2):
        '''
        Write Golden Software Surfer 7 binary grid formats.

        version : Version number of the file format. Can be set to 1 or 2.
            If the version field is 1, then any value >= BlankValue will be blanked using Surfer’s blanking value, 1.70141e+038.
            If the version field is 2, then any value == BlankValue will be blanked using Surfer’s blanking value, 1.70141e+038.

        '''

        # Recovering grid info
        nCol = grid.nCol
        nRow = grid.nRow
        xLL = grid.xLL
        yLL = grid.yLL
        xSize = grid.xSize
        ySize = grid.ySize
        zMin = grid.zMin
        zMax = grid.zMax

        # Converting nans to blanks
        Rotation = 0
        BlankValue = 1.70141e38
        data = grid.data
        data[np.isnan(data)] = BlankValue

        with open(filename, "wb") as file:

            # Headers
            HeaderSize = 4
            HeaderVersion = version
            file.write(struct.pack('4s', b'DSRB'))  # DSRB: Surfer 7 binary grid tag

            file.write(struct.pack('<l', HeaderSize))  # Size of Header section
            file.write(struct.pack('<l', HeaderVersion))  # Header Section Version
                                                           # 1: then any value >= BlankValue will be blanked.
                                                           # 2: then any value == BlankValue will be blanked.

            # Grid section
            file.write(struct.pack('4s', b'GRID'))  # Tag: ID indicating a grid section
            file.write(struct.pack('<l', 72))  # Tag: Length in bytes of the grid section

            file.write(struct.pack('<l', nRow))  # long
            file.write(struct.pack('<l', nCol))  # long
            file.write(struct.pack('<d', xLL))  # double
            file.write(struct.pack('<d', yLL))  # double
            file.write(struct.pack('<d', xSize))  # double
            file.write(struct.pack('<d', ySize))  # double
            file.write(struct.pack('<d', zMin))  # double
            file.write(struct.pack('<d', zMax))  # double
            file.write(struct.pack('<d', Rotation))  # double
            file.write(struct.pack('<d', BlankValue))  # double

            # Data section
            datalen = nCol*nRow*8
            if datalen != nCol*nRow*8:
                raise GridError(('Invalid Surfer 7 binary grid file '
                                 'Inconsistency between expected DATA '
                                 'Length and nRow, nCol. '
                                 'Expected length is (%d) but %s encountered.') %(nCol*nRow*8, datalen)
                                 )

            file.write(struct.pack('4s', b'DATA'))  # Tag: ID indicating a data section
            file.write(struct.pack('<l', datalen))  # Tag: Length in bytes of the data section (nRows x nCcol x 8 bytes per double)

            for row in range(nRow):  # Y
                for col in range(nCol): # X
                    file.write(struct.pack('<d', float(data[row][col])))  # float

    def _write_surfer6bin(self, filename, grid):
        ''' Write Golden Software Surfer 6 binary grid formats. '''

        # Recovering grid info
        nCol = grid.nCol
        nRow = grid.nRow
        xMin = grid.getXmin()
        xMax = grid.getXmax()
        yMin = grid.getYmin()
        yMax = grid.getYmax()
        zMin = grid.zMin
        zMax = grid.zMax

        # Converting nans to blanks
        BlankValue = 1.70141e38
        data = grid.data
        data[np.isnan(data)] = BlankValue

        with open(filename, "wb") as file:

            # Surfer 6 binary grid tag
            file.write(struct.pack('4s', b'DSBB'))  # DSBB

            # Grid info
            file.write(struct.pack('<h', nCol))  # short
            file.write(struct.pack('<h', nRow))  # short
            file.write(struct.pack('<d', xMin))  # double
            file.write(struct.pack('<d', xMax))  # double
            file.write(struct.pack('<d', yMin))  # double
            file.write(struct.pack('<d', yMax))  # double
            file.write(struct.pack('<d', zMin))  # double
            file.write(struct.pack('<d', zMax))  # double

            # Data
            for row in range(nRow):  # Y
                for col in range(nCol): # X
                    file.write(struct.pack('<f', float(data[row][col]))) # float

    def _write_surfer6ascii(self, filename, grid):
        ''' Write Golden Software Surfer 6 ascii grid formats. '''

        # Recovering grid info
        nCol = grid.nCol
        nRow = grid.nRow
        xMin = grid.getXmin()
        xMax = grid.getXmax()
        yMin = grid.getYmin()
        yMax = grid.getYmax()
        zMin = grid.zMin
        zMax = grid.zMax

        # Converting nans to blanks
        BlankValue = 1.70141e38
        data = grid.data
        data[np.isnan(data)] = BlankValue

        with open(filename, "w") as file:

            # Surfer 6 ascii grid tag
            file.write("DSAA\n")  # DSAA

            # Headers ([[nx, ny], [xlo, xhi], [ylo, yhi], [zlo, zhi]]
            headers = [[nCol, nRow], [xMin, xMax], [yMin, yMax], [zMin, zMax]]
            for row in headers:
                file.write('{:g} {:g}\n'.format(*row))  # "*row" unpacks the list : format()

            # Data
            for row in data:
                frmt = '{:g} '*(nCol-1) + '{:g}\n'  # format val1 val2 ... valnCol\n
                file.write(frmt.format(*row))  # "*row" unpacks the list : format()

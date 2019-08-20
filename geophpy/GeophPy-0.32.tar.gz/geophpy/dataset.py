# -*- coding: utf-8 -*-
'''
   GeophPy.dataset
   ---------------

   DataSet Object constructor and methods.

   :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
   :license: GNU GPL v3.

'''

from __future__ import absolute_import
import geophpy.plotting.plot as plot
import geophpy.plotting.correlation as correlation
import geophpy.plotting.colormap as colormap
import geophpy.plotting.histo as histo
import geophpy.plotting.destriping as destriping
import geophpy.plotting.spectral as spectral
import geophpy.operation.general as genop
import geophpy.processing.general as genproc
import geophpy.processing.magnetism as magproc
import geophpy.filesmanaging.files as iofiles
import geophpy.geoposset as geopos
import geophpy.geopositioning.kml as kml
import geophpy.geopositioning.raster as raster
import geophpy.geopositioning.general as gengeopositioning
import os

#---------------------------------------------------------------------------#
# Informations about DataSet Object                                         #
#---------------------------------------------------------------------------#
class Info:
    ''' Class to sotre grid informations.

    Attributes
    ----------
    x_min : float
        Grid minimum x values.

    x_max : float
        Grid maximum x values.

    y_min : float
        Grid minimum y values.

    y_max : float
        Grid maximum y values.

    z_min : float
        Grid minimum z values.

    z_max : float
        Grid maximum z values.

    x_gridding_delta : float
        Grid stepsize in the x_direction.

    y_gridding_delta : float
        Grid stepsize in the y_direction.

    gridding_interpolation : str
        Interpolation method used for gridding.

    plottype : str
        Grid plot type.

    cmapname : str
        Grid plot colormap name.

    '''

##    def __init__(self, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None ,zmax=None, dx=None, dy=None,
##                 interp=None, plottype ='2D-SURFACE', cmap='Greys'):
##        self.x_min = xmin
##        self.x_max = xmax
##        self.y_min = ymin
##        self.y_max = ymax
##        self.z_min = zmin
##        self.z_max = zmax
##        self.x_gridding_delta = dx
##        self.y_gridding_delta = dy
##        self.gridding_interpolation = interp
##        self.plottype = plottype
##        self.cmapname = cmap

    x_min = None
    x_max = None
    y_min = None
    y_max = None
    z_min = None
    z_max = None
    x_gridding_delta = None
    y_gridding_delta = None
    gridding_interpolation = None
    plottype = (plot.gettypelist())[0]
    cmapname = 'Greys'


#---------------------------------------------------------------------------#
# Fields names and values about DataSet Object                              #
#---------------------------------------------------------------------------#
class Data:
    ''' Class to sotre data.

    Attributes
    ----------
    fields : list of str
        Field names corresponding to the data values ('x', 'y', 'vgrad').

    values : array-like
        Ungridded data values.

    z_image : 2-D array-like.
        Gridded data values.

    easting_image :
        ???
    northing_image :
        ???

    '''

    fields = None  # name for the x, y and z fields 
    values = None  # ungridded data values
    z_image = None  # gridded data values
    easting_image = None    # easting grid (used if the dataset is georeferenced)
    northing_image = None   # northing grid (used if the dataset is georeferenced)
    easting  = None  # ungridded dataset easting
    northing = None  # ungridded data orthing


#---------------------------------------------------------------------------#
# Coordinates Object in local and utm referencing                           #
#---------------------------------------------------------------------------#
class GeoRefPoint:
    def __init__(self, easting=None, northing=None):
        self.utm_easting = easting
        self.utm_northing = northing


#---------------------------------------------------------------------------#
# Georeferencement System Object between local and geographics positions    #
#---------------------------------------------------------------------------#
class GeoRefSystem:
    active = False          # data set georeferencement status
    refsystem = None        # 'UTM', 'WGS84', ...
    utm_zoneletter = None   # E -> X
    utm_zonenumber = None   # 1 -> 60
    points_list = []        # list of points, [[num1, lon1 or eastern1, lat1 or northern1, x, y], ...]


#---------------------------------------------------------------------------#
# DataSet Object                                                            #
#---------------------------------------------------------------------------#
class DataSet(object):
   '''
   Creates a DataSet Object to process and display data.

   info = Info()
   data = Data()
   georef = GeoRefSystem()
   '''

   def __init__(self):
       # Why empty and not the content of _new here ?
       '''
       self.info = Info()
       self.data = Data()
       self.georef = GeoRefSystem()
       '''
       pass

   @classmethod
   def _new(cls):
      '''
      Creates a new empty data set
      '''
      dataset = cls()
      dataset.info = Info()
      dataset.data = Data()
      dataset.georef = GeoRefSystem()
      return dataset

   #---------------------------------------------------------------------------#
   # DataSet file management                                                   #
   #---------------------------------------------------------------------------#
   ###
   ##
   # As a class constructor, should probably a classe method, rigth ?
   ##
   ###
   @staticmethod
   def from_file(filenameslist, fileformat=None, delimiter=None, x_colnum=1, y_colnum=2, z_colnum=3, skipinitialspace=True, skip_rows=0, fields_row=1):
      ''' Build a DataSet Object from a file.

      Parameters:

      :filenameslist: list of files to open
                      ['file1.xyz', 'file2.xyz' ...]
                      or
                      ['file*.xyz'] to open all files with filename beginning by "file" and ending by ".xyz"

      :fileformat: format of files to open (None by default implies automatic determination from filename extension)

      Note: all files must have the same format

      :delimiter: pattern delimitting fields within one line (e.g. '\t', ',', ';' ...)

      :x_colnum: column number of the X coordinate of the profile (1 by default)

      :y_colnum: column number of the Y coordinate inside the profile (2 by default)

      :z_colnum: column number of the measurement profile (3 by default)

      :skipinitialspace: if True, several contiguous delimiters are equivalent to one

      :skip_rows: number of rows to skip at the beginning of the file, i.e. total number of header rows (1 by default)

      :fields_row: row number where to read the field names ; if -1 then default field names will be "X", "Y" and "Z"

      Returns:

      :success: true if DataSet Object built, false if not

      :dataset: DataSet Object build from file(s) (empty if any error)

      Example:

      success, dataset = DataSet.from_file("file.csv")
      '''

      # Dispatch method ########################################################
      class From():

         @staticmethod
         def ascii():
            return iofiles.from_ascii(dataset, filenameslist, delimiter=delimiter, x_colnum=x_colnum, y_colnum=y_colnum, z_colnum=z_colnum, skipinitialspace=skipinitialspace, skip_rows=skip_rows, fields_row=fields_row)

         @staticmethod
         def netcdf():
            return iofiles.from_netcdf(dataset, filenameslist, x_colnum=x_colnum, y_colnum=y_colnum, z_colnum=z_colnum)

         @staticmethod
         def surfer():
            return iofiles.from_grd(dataset, filenameslist, gridtype=None)

      # Create a new dataset ###################################################
      dataset = DataSet._new()
      # if class method:  dataset = cls() ? 

      # Choose the input file format ###########################################
      if fileformat is None:
         # ...TBD... Determine the format from file header
         pass

      if fileformat is None:
         # Determine the format from filename extension
         file_extension = os.path.splitext(filenameslist[0])[1]
         fileformat = format_chooser.get(file_extension, 'ascii')

      # Read the dataset from input file #######################################
      if fileformat in fileformat_getlist():
         readfile = getattr(From, fileformat)
         error    = readfile()

      else:
         # Undefined file format ###############################################
         # ...TBD... raise an error here !
         error = 1

      # Return the dataset and error code ######################################
      if error==0:
         success = True
      else:
         success = False

      return success, dataset

   ###
   ##
   # ... Still Under Construction ...
   ##
   ###
##   @classmethod
##   def from_cmdfile(cls, filenameslist, param='cond1'):
##       ''' Build a DataSet Object from Gf Instrument CMD ascii file.
##
##       Reads both Gf Instrument CMD interpolated and not interpolated
##       Gf Instrument CMD ascii file format.
##
##       Parameter
##       ---------
##       param : {'cond1','inph1','cond2','inph2','cond3','inph3'}
##           Parameter to be read.
##
##       Returns
##       -------
##       success : bool
##           True if DataSet Object was built, false otherwise.
##
##       dataset: DataSet Object built from the file(s) (empty if any error)
##
##       Example
##       -------
##       success, dataset = DataSet.from_cmdfile("DataCmdMini.dat")
##
##       '''
##
##       # Creating empty dataset
##       dataset = cls()
##       dataset.info = Info()
##       dataset.data = Data()
##       dataset.georef = GeoRefSystem()
##
##       # Reading cmd file and populating dataset
##       error_code = iofiles.from_cmdfile(dataset, filenameslist, param=param)
##
##       # Return the dataset and error code #####################################
##       if error_code==0:
##           success = True
##       else:
##           success = False
##
##       return success, dataset
      
   def to_file(self, filename, fileformat=None, delimiter='\t', description=None, gridtype='surfer7bin'):
      '''
      Save a DataSet Object to a file.

      Parameters :

      :filename: name of file to save.

      :fileformat: format of output file ...

      :delimiter: delimiter between fields in a line of the output file, '\t', ',', ';', ...

      :gridtype: str {'surfer7bin', 'surfer6bin', 'surfer6ascii'}, optional
          Format of the grid file to write. By default 'surfer7bin'.

      Returns :

      :success: boolean

      '''
      # Dispatch method ##############################################
      class To():
         @staticmethod
         def ascii():
            return iofiles.to_ascii(self, filename, delimiter=delimiter)

         @staticmethod
         def netcdf():
            return iofiles.to_netcdf(self, filename, description=description)

         @staticmethod
         def surfer():
            return iofiles.to_grd(self, filename, gridtype=gridtype)

      # Choose the dataset format ####################################
      if fileformat is None:
         # Determine the format from filename extension
         file_extension = os.path.splitext(filename)[1]
         fileformat = format_chooser.get(file_extension, None)

      # Write the dataset to file ####################################
      if fileformat in fileformat_getlist():
         writefile = getattr(To, fileformat)
         error     = writefile()
      else:
         # Undefined file format #####################################
         # ...TBD... raise an error here !
         error = 1

      # Return the error code ########################################
      if (error == 0):
         success = True
      else:
         success = False
      return success

   #---------------------------------------------------------------------------#
   # DataSet Plotting                                                          #
   #---------------------------------------------------------------------------#
   def plot(self, plottype='2D-SCATTER', cmapname=None, creversed=False,
            fig=None, filename=None, cmmin=None, cmmax=None, interpolation='bilinear',
            levels=100, cmapdisplay=True, axisdisplay=True, labeldisplay=True,
            pointsdisplay=False, dpi=None, transparent=False, logscale=False,
            rects=None, points=None, marker='+', markersize=None):
       ''' 2D representation of the dataset.

       Parameters
       ----------
       plottype : str, {'2D-SCATTER', '2D-SURFACE', '2D-CONTOUR', '2D-CONTOURF', '2D-POSTMAP'}
           Plot type for the data representation.
           Plot type can be

           ``2D-SCATTER``
               (by default) ungridded data values are dispay in a scatter plot.
               Plot type 'SCATTER', 'SCAT' and 'SC' are also recognised.

           ``2D-SURFACE``
               Gridded data values are dispay in a surface (image) plot.
               Plot type 'SURFACE', 'SURF' and 'SF' are also recognised.

           ``2D-CONTOUR``
               Gridded data values are dispay in a UNFILLED contour plot.
               If this plot type is used, you can specify the number of
               contours used with the ``levels`` keyword.
               Plot type 'CONTOUR', 'CONT' and 'CT' are also recognised.

           ``2D-CONTOURF``
               Gridded data values are dispay in a FILLED contour plot.
               If this plot type is used, you can specify the number of
               contours used with the ``levels`` keyword.
               Plot type 'CONTOURF', 'CONTF' and 'CF' are also recognised.

           ``2D-POSTMAP``
               Ungridded data position are dispay in a scatter plot.
               It is different from the '2D-SCATTER' plot because
               the data value is not represented (all point have the same color).
               Plot type 'POSTMAP', 'POST' and 'PM' are also recognised.

       cmapname : str
           Name of the color map to be used 'gray' for example.
           To use a reversed colormap, add '_r' at the end of the colormap name ('gray_r')
           or set ``creversed`` to ``True``. 

       creversed : bool
           Flag to add '_r' at the end of the color map name to reverse it.

       fig : Matplotlib figure object
           Figure to plot, None by default to create a new figure.
           If a figure object is provided, it wiil be cleared before displaying the current data.

       filename : str or None
           Name of file to save the figure, None (by default).

       cmmin : scalar
           Minimal value to display in the color map range.

       cmmax : scalar
           Maximal value to display in the color map range.

       interpolation : str,
           Interpolation method used for the pixel interpolation ('bilinear' by default).
           If interpolation is 'none', then no interpolation is performed for the display.
           Supported values are 'none', 'nearest', 'bilinear', 'bicubic',
           'spline16', 'spline36', 'hanning', 'hamming', 'hermite', 'kaiser',
           'quadric', 'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos'.

       levels : (int or array-like)
           Determines the number and positions of the contour lines / regions.
           If an int n, use n data intervals; i.e. draw n+1 contour lines. The level heights are automatically chosen.
           If array-like, draw contour lines at the specified levels. The values must be in increasing order.

       cmapdisplay : bool
           True to display colorbar, False to hide the colorbar.

       axisdisplay : bool
           True to display axis (and their labels), False to hide axis (and labels).

       labeldisplay : bool
           True to display labels on axis, False to hide labels on axis.

       pointsdisplay : bool
           True to display grid points.

       dpi : int or None
           Definition ('dot per inch') to use when saving the figure into a file (None by default).

       transparent : bool
           Flag to manage transparency when saving the figure into a file (False by default).

       logscale : bool
           Flag to use a logarithmic color scale.

       rects: None or array_like
           Coordinates of additional rectanngles to display:
           [[x0, y0, w0, h0], [x1, y1, w1, h1], ...].
           None by default.
           
       points: None or array_like
           Coordinates of additional points to display:
           [[x0, y0], [x1, y1], ...]. None by default.

       marker: str
           Matplotlib marker style for data point display.

       markersize: scalar
           Size for the marker for data point display.

       Returns
       -------
       fig : Matplotlib Figure Object
           Dataset map figure.

       cmap : Matplotlib ColorBar Object
           Colorbar associated with the figure if ``cmapdisplay`` is ``True``, ``None`` otherwise.

       '''

      # Updating dataset colormap name
       if cmapname is None:
           cmapname = self.info.cmapname

       self.info.cmapname = cmapname

       return plot.plot(self, plottype, cmapname, creversed=creversed, fig=fig, filename=filename, cmmin=cmmin, cmmax=cmmax, interpolation=interpolation, levels=levels, cmapdisplay=cmapdisplay, axisdisplay=axisdisplay, labeldisplay=labeldisplay, pointsdisplay=pointsdisplay, dpi=dpi, transparent=transparent, logscale=logscale, rects=rects, points=points, marker=marker, markersize=markersize)

   def histo_getlimits(self, valfilt=False):
       ''' Return the data min and max values.

       Parameters
       ----------
       valfilt : bool
           If True, min and max are taken from data values. 
           Otherxise, min and max are taken from data z_image.

       Returns
       -------
       zmin, zmax : float
           Data min and max values.

       '''

       return histo.getlimits(self, valfilt=valfilt)

###
###
##
# TO IMPLEMENT in the next version
##
###
##   def histo_fit(self):
##       ''' '''
##       return

   ### Change name to plot_histo
   def histo_plot(self, fig=None, filename=None, zmin=None, zmax=None, cmapname=None, creversed=False, cmapdisplay=False, coloredhisto=True, dpi=None, transparent=False, valfilt=False):
       ''' Plot the dataset histogram.

       Parameters
       ----------
       fig : Matplotlib figure object
           Figure to use for the plot, None (by default) to create a new figure.

       filename : str or None
           Name of file to save the figure, None (by default).

       zmin, zmax : float or None
           Minimal and maximal values to represent.

       cmapname : str
           Name of the color map to be used 'gray' for example.
           To use a reversed colormap, add '_r' at the end of the colormap name ('gray_r')
           or set ``creversed`` to ``True``. 

       creversed : bool
           Flag to add '_r' at the end of the color map name to reverse it.

       cmapdisplay : bool
           Flag to display a color bar (True by default).

       coloredhisto : bool
           Flag to color the histogram using the given colormap (True by default). If False, balck will be used.

       dpi : int or None
           Definition ('dot per inch') to use when saving the figure into a file (None by default).

       transparent : bool
           Flag to manage transparency when saving the figure into a file (False by default).

       valfilt : bool
           If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`
           (False By default).

       Returns
       -------
       fig : Matplotlib Figure Object
           Dataset histogram figure.

       cmap : Matplotlib ColorBar Object
           Colorbar associated with the figure if ``cmapdisplay`` is ``True``, ``None`` otherwise.

       '''

       # Updating dataset colormap name
       if cmapname is None:
           cmapname = self.info.cmapname

       self.info.cmapname = cmapname

       return histo.plot(self, fig=fig, filename=filename, zmin=zmin, zmax=zmax, cmapname=cmapname, creversed=creversed, cmapdisplay=cmapdisplay, coloredhisto=coloredhisto, dpi=dpi, transparent=transparent, valfilt=valfilt)

   ### Change name to plot_corrmap
   def correlation_plotmap(self, method="Crosscorr" , cmapname='jet',
                           fig=None, filename=None, dpi=None, transparent=False, showenvelope=False, cmapdisplay=True):
       ''' Plot profile-to-profile correlation map.

       Parameters
       ----------
       method : str, {'Crosscorr', 'Pearson', 'Spearman' or 'Kendall'}
           Correlation method.

       cmapname : str or None
           Name of the color map to be used, 'gray_r' for example.

       fig : Matplotlib figure object
           Figure to use for the plot, None (by default) to create a new figure.

       filename : str or None
           Name of the file to save the figure, None (by default).

       dpi : int or None
           Definition ('dot per inch') to use when saving the figure into a file (None by default).

       transparent : bool
           Flag to manage transparency when saving the figure into a file (False by default).

       showenvelope : bool
           Flag to display the correlation map envelope.

       cmapdisplay : bool
           Flag to display a color bar (True by default).

       Returns
       -------
       fig : Matplotlib Figure Object
           Dataset profile-to-profile correlation map.

       '''

       return correlation.plotmap(self, method=method, cmapname=cmapname, fig=fig, filename=filename,
                                  dpi=dpi, transparent=transparent, showenvelope=showenvelope)

   ### Change name to plot_corrsum
   def correlation_plotsum(self, fig=None, filename=None, method='Crosscorr', dpi=None, transparent=False,
                           showenvelope=False, showfit=False):
       '''
       Plot correlation sum.

       Parameters
       ----------
       fig : Matplotlib figure object
           Figure to use for the plot, None (by default) to create a new figure.

       filename : str or None
           Name of the file to save the figure, None (by default).

       method : str, {'Crosscorr', 'Pearson', 'Spearman' or 'Kendall'}
           Correlation method.

       transparent : bool
           Flag to manage transparency when saving the figure into a file (False by default).
           (False By default).

       showenvelope : bool
           Flag to display the curve envelope.

       showfit : bool
           Flag to display the curve gausian beest fit.

       Returns
       -------
       fig : Matplotlib Figure Object
           Dataset profile-to-profile correlation sum.

       '''

       return correlation.plotsum(self, fig=fig, filename=filename,
                                  method=method, dpi=dpi, transparent=transparent,
                                  showenvelope=showenvelope, showfit=showfit)

   ### Change name to plot_meantrack
   def meantrack_plot(self, fig=None, filename=None, Nprof=0, setmin=None, setmax=None,
                      method='additive', reference='mean', config='mono', Ndeg=None,
                      plotflag='raw', dpi=None, transparent=False):
      '''
      Plot the dataset mean cross-track profile before and after destriping.

      Parameters :

      :fig: figure to plot, None by default to create a new figure. `matplotlib.figure.Figure`

      :filename: Name of the histogram file to save, None if no file to save.

      :Nprof: number of profiles to compute the reference mean 

      :setmin: float, While computing the mean, do not take into account data values lower than *setmin*.

      :setmax: float, While computing the mean, do not take into account data values greater than *setmax*.

      :method: destriping method (additive or multiplicative)

      :reference: destriping reference (mean and standard deviation or median and interquartile range)

      :config: destriping configuration ('mono' sensor: only offset matching (mean / median), 'multi' sensor: both offset and gain (standard deviation/interquartile range))

      :plotflag: str, {'raw', 'destriped', 'both'} to plot raw, destriped or both data

      :Ndeg: polynomial degree of the curve to fit	

      :transparent: True to manage the transparency.

      Returns :

      :fig: Figure Object

      Note
      ----

      The mean cross-track profile is the profile composed the mean of each
      profile in the dataset.

      '''
      
      return destriping.plot_mean_track(self, fig=fig, filename=filename, Nprof=Nprof, setmin=setmin, setmax=setmax, method=method, reference=reference, config=config,Ndeg=Ndeg, plotflag=plotflag, dpi=dpi, transparent=transparent)

   ### Change name to plot_sprectum
   def spectral_plotmap(self, fig=None, filename=None, dpi=None, plottype='magnitude', logscale=False, cmapdisplay=True, axisdisplay=True, lines=None):
       '''
       Plot the dataset 2-D Fourier Transform.

       Paramters
       ---------
       fig: figure to plot,
           Figure used for the plot. None by default to create a new figure.

       filename: str
           Name of the file to save the figure. None (default) if no file to save.

       dpi: int
           'dot per inch' definition of the picture file if filename is not None.

       plottype: str {'magnitude' or 'amplitude','power',phase','real','imag'}
           Spectrum composante to plot.

       logscale: bool
           True for a plot with a logarithmic colorscale.

       cmapdisplay: bool
           True to display colorbar, False to hide the colorbar.

       axisdisplay: bool
           True to display axis, False to hide the axis.
       '''
       return spectral.plotmap(self, fig=fig, filename=filename, dpi=dpi, plottype=plottype, logscale=logscale, cmapdisplay=cmapdisplay, axisdisplay=axisdisplay, lines=lines)

   def plot_directional_filter(self, cmapname=None, creversed=False, fig=None, filename=None, dpi=None, cmapdisplay=True, axisdisplay=True, paramdisplay=False, cutoff=100, azimuth=0, width=2):
       '''
       Plot the dataset 2-D directional filter.

       Paramters
       ---------
       cmapname : str
           Name of the color map to be used, 'gray_r' for example.

       creversed : bool
           True to reverse the color map (add '_r' at the cmapname).
      
        fig : figure to plot,
            Figure used for the plot. None by default to create a new figure.

        filename : str
            Name of the file to save the figure. None (default) if no file to save.

        dpi : int
            'dot per inch' definition of the picture file if filename is not None.

        cmapdisplay : bool
            True to display colorbar, False to hide the colorbar.

        axisdisplay : bool
            True to display axis, False to hide the axis.

        axisdisplay : bool
            True to display filter parameter in the title.

        shape : tuple
            Filter shape.
    
        cutoff : ndarray
            Input array to filter.

        azimuth : scalar
            Directional filter azimuth angle in degree.

        width : integer
            Gaussian filter cutoff frequency.

       Returns
       -------
       fig : Matplotlib Figure Object

       cmap : Matplotlib ColorMap Object

       '''

       return spectral.plot_directional_filter(self, cmapname=cmapname, creversed=creversed, fig=fig, filename=filename, dpi=dpi, cmapdisplay=cmapdisplay, axisdisplay=axisdisplay, paramdisplay=paramdisplay,
                                               cutoff=cutoff, azimuth=azimuth, width=width)

   #---------------------------------------------------------------------------#
   # DataSet Operations                                                        #
   #---------------------------------------------------------------------------#
   def copy(self):
       '''
       To duplicate a DataSet Object.

       Parameters:

       :dataset: DataSet Object to duplicate

       Returns:

       :newdataset: duplicated DataSet Object
       '''
       
       return genop.copy(self)

   def interpolate(self, interpolation='none', x_step=None, y_step=None, x_prec=2, y_prec=2, x_frame_factor=0., y_frame_factor=0.):
       ''' Dataset gridding.

       Parameters
       ----------
       interpolation : str {'none', 'nearest', 'linear', 'cubic'}
           Method used to grid the dataset. Can be:
           
           ``none``
               (by default) simply projects raw data on a regular grid without interpolation.
               Holes are filled with NaNs and values falling in the same grid cell are averaged.

           ``nearest``
               return the value at the data point closest to
               the point of interpolation.

           ``linear``
               tesselate the input point set to n-dimensional
               simplices, and interpolate linearly on each simplex.

           ``cubic``
               return the value determined from a
               piecewise cubic, continuously differentiable (C1), and
               approximately curvature-minimizing polynomial surface.

       x_step, y_step : float or None
           Gridding step in the x and y direction.
           Use None (by default) to estimate the median x- and y-step from data values.

       x_prec, y_prec : int or None
           Decimal precision to keep for the grid computation.
           None (by default) to use the maximal number of decimal present in the data values coordinates.

       x_frame_factor :
           Frame extension coefficient along x axis (e.g. 0.1 means xlength +10% on each side, i.e. xlength +20% in total) ; pixels within extended borders will be filled with "nan"

       y_frame_factor :
           Frame extension coefficient along y axis (e.g. 0.45 means yheight +45% top and bottom, i.e. yheight +90% in total) ; pixels within extended borders will be filled with "nan"

       Returns
       -------
       Gridded DataSet object.

       '''

       return genop.interpolate(self, interpolation=interpolation, x_step=x_step, y_step=y_step, x_prec=x_prec, y_prec=y_prec, x_frame_factor=x_frame_factor, y_frame_factor=y_frame_factor)

   def sample(self):
       ''' Re-sample data at ungridded sample position from gridded Z_image.

       Re-sample ungridded values from gridded Z_image using a
       cubic spline spline interpolation.

       '''

       return genop.sample(self)

   def regrid(self, x_step=None, y_step=None, method='cubic'):
       ''' Dataset re-gridding.

       During regridding, a copy of the dataset is re-sampled
       (see :meth:`~geophpy.dataset.DataSet.sample`)
       and interpolated with the given x and y-steps. 

       Parameters
       ----------
       x_step, y_step : float or None
           Gridding step in the x and y direction.
           Use None (by default) to resample current grid by a factor 2 (step_new = step_old*0.5).

       method : str {'cubic', 'nearest', 'linear'}
           Method used to re-grid the dataset. see :meth:`~geophpy.dataset.DataSet.interpolate`

       Returns
       -------
       Re-gridded DataSet object.

       Note
       ----
       Only the grid is affected and the ungriddedd data values are kept unchanged.
       to propagate a change in the ungriddedd data values,
       you may want to use the filters ``valfilt`` keyword or the association of
       :meth:`~geophpy.dataset.DataSet.sample` and
       :meth:`~geophpy.dataset.DataSet.sample`.

       See Also
       --------
       sample, interpolate

       '''

       return genop.regrid(self, x_step=None, y_step=None, method='cubic')

   def stats(self, valfilt=True, valmin=None, valmax=None):
       '''
       Computes the dataset basic statistics.

       Parameters:

       :dataset: DataSet Object from which to compute stats.

       :valfilt: if set to True, computes on data.values instead of data.z_image.

       :valmin, valmax: Consider only data values between valmin and valmax.

       Returns:

       :mean, std, median: array arithmetic mean, standard deviation and median.

       :Q1, Q3: dataset 1st and 3rd quartiles (25th and 75th percentiles).

       :IQR: dataset interquartile range (Q3 - Q1).
       '''

       return genop.stats(self, valfilt=valfilt, valmin=valmin, valmax=valmax)

   def add(self, val=0, valfilt=True, zimfilt=True):
       '''
       Add a constant to the dataset Values and Z_image.

       Parameters:

       :val: constant to add.

       :valfilt: flag to add constant on dataset values.

       :zimfilt: flag to add constant on dataset z_image.
       '''

       return genop.add_constant(self, constant=val, valfilt=valfilt, zimfilt=zimfilt)

   def times(self, val=1, valfilt=True, zimfilt=True):
       '''
       Multiply by a constant the dataset Values and Z_image
       
       Parameters:

       :val: constant to multiply by.

       :valfilt: flag to add constant on dataset values.

       :zimfilt: flag to add constant on dataset z_image.
       ''' 

       return genop.times_constant(self, constant=val, valfilt=valfilt, zimfilt=zimfilt)

   def setmedian(self, median=None, method='additive'):
       '''
       Set the dataset values and Z_image to a given value
       (for instance zero for zero median surveys).

       Parameters:

       :median: target value to set the dataset median to.

       :method: method used to set the median ('additive' or 'multiplicative').

       :profilefilter: ...TBD... True: set each survey profiles median to 'median'.
                       False: set the global survey median to 'median'. 
       '''

       return genop.setmedian(self, median=median, method=method)

   def setmean(self, mean=None, method='additive'):
       '''
       Set the dataset values and Z_image to a given value
       (for instance zero for zero median surveys).

       Parameters:

       :mean: value to set the dataset mean to.

       :method: method used to set the mean ('additive' or 'multiplicative').

       :profilefilter: ...TBD... True: set each survey profiles mean to 'mean'.
                       False: set the global survey mean to 'mean'. 
       '''

       return genop.setmean(self, mean=mean, method=method)
       
   def translate(self, shiftx=0, shifty=0):
       '''
       Dataset translation.

       Parameters:
    
       :shiftx: Constant to apply to the x-abscisse.
    
       :shifty: Constant to apply to the y-abscisse.

       Returns:

       Translated DataSet object.
       '''

       return genop.translate(self, shiftx=shiftx, shifty=shifty)

   def rotate(self, angle=0, center=None):
       '''
       Dataset rotation (clockwise).

       Parameters
       ----------
    
       angle: float
           Rotation angle (in °).
       
       center: str {None, 'BL', 'BR', 'TL, 'TR'}
           Center of rotation: 'BL', 'BR', 'TL and 'TR' for bottom left,
           bottom rght, top left and top right corner.
           If None,  the dataset centroid will be used.

       Returns:

       Rotated DataSet object.
       '''

       return genop.rotate(self, angle=angle, center=center)


##   def matchedges(self, datasets, matchmethod='equalmedian', setmed=None, valfilt=True, setmethod='additive'):
##       '''
##       '''
##       return genop.matchedges(datasets, matchmethod=matchmethod, setmed=setmed, valfilt=valfilt, setmethod=setmethod)

   #staticmethod
   #def merge(datasetlist, matchmethod=None, setval=None, setmethod='additive', meanrange=None):
   def merge(self, datasets, matchmethod=None, setval=None, setmethod='additive', meanrange=None):
       '''
       Merge datasets together.

       Parameters
       ----------
       datasetlist : tuple or list.
           Sequence of datasets to merge. Each DataSet Object must have the same coordinates system.

       matchmethod :

       setmethod : {'additive', 'multiplicative'}
           Method used to merge the datasets ## TODO Complete docstring.

       setval :

       meanrange :

       Returns
       -------
       merged :  new DataSet Object.
       
       '''
       # Empty Merge DataSet
       datasetout = DataSet._new()
       genop.merge(datasetout, datasets, matchmethod=matchmethod, setval=setval, setmethod=setmethod, meanrange=meanrange)

       return datasetout

   #---------------------------------------------------------------------------#
   # DataSet Coordinates/values                                                #
   #---------------------------------------------------------------------------#
   def get_xgrid(self):
       ''' Return dataset x-coordinate matrix of the Z_image. '''

       return genop.get_xgrid(self)

   def get_ygrid(self):
       ''' Return dataset y-coordinate matrix of the Z_image. '''

       return genop.get_ygrid(self)

   def get_xygrid(self):
       ''' Return dataset x- and y-coordinate matrices of the Z_image. '''

       return genop.get_xygrid(self)

   def get_grid_values(self):
       ''' Return dataset Z_image. '''

       return self.data.z_image

   def get_gridcorners(self):
       ''' Return dataset grid corners coordinates.

       Returns ``None`` if no interpolation was made.
       Use :meth:~geophpy.dataset.DataSet.get_boundingbox`
       to get the ungridded data values' bounding box.

       '''

       return genop.get_gridcorners(self)

   def get_gridextent(self):
       ''' Return dataset grid extent. '''

       return genop.get_gridextent(self)

   def get_xvect(self):
       ''' Return dataset x-coordinate vector of the Z_image. '''

       return genop.get_xvect(self)

   def get_yvect(self):
       ''' Return dataset y-coordinate vector of the Z_image. '''

       return genop.get_yvect(self)

   def get_xyvect(self):
       ''' Return dataset x- and y-coordinate vectors of the Z_image. '''

       return genop.get_xyvect(self)

   def get_xvalues(self):
       ''' Return the x-coordinates from the dataset values. '''

       return genop.get_xvalues(self)

   def get_yvalues(self):
       ''' Return the y-coordinates from the dataset values. '''

       return genop.get_yvalues(self)

   def get_values(self):
       ''' Return the dataset values. '''

       return genop.get_values(self)

   def get_xyvalues(self):
       ''' Return the x- and y-coordinates from the dataset values. '''

       return genop.get_xyvalues(self)

   def get_xyzvalues(self):
       ''' Return both the x, y-coordinates and dataset ungridded values. '''

       return genop.get_xyzvalues(self)
   
   def get_boundingbox(self):
       ''' Return the coordinates (BL, BR, TL, TR) of the box bouding the data values. '''

       return genop.get_boundingbox(self)

   def get_median_xstep(self, prec=2):
       ''' Return the median step between two distinct x values rounded to the given precision. '''

       return genop.get_median_xstep(self, prec=prec)

   def get_median_ystep(self, prec=2):
       ''' Return the median step between two distinct y values rounded to the given precision. '''

       return genop.get_median_ystep(self, prec=prec)

   def get_median_xystep(self, x_prec=2, y_prec=2):
       ''' Return the median steps between two distinct x and y values rounded to the given precisions. '''

       return genop.get_median_xystep(self, x_prec=x_prec, y_prec=y_prec)

   def get_georef_xvalues(self):
       ''' Return the easting coordinates from the dataset values. '''

       return self.data.easting

   def get_georef_yvalues(self):
       ''' Return the northing coordinates from the dataset values. '''

       return self.data.northing

   def get_georef_xyvalues(self):
       ''' Return the easting and northing coordinates from the dataset values. '''

       return self.data.easting, self.data.northing

   def get_georef_xgrid(self):
       ''' Return the easting coordinates matrices of the Z_image. '''

       return self.data.easting_image

   def get_georef_ygrid(self):
       ''' Return the northing coordinates matrices of the Z_image. '''

       return self.data.northing_image

   def get_georef_xygrid(self):
       ''' Return the easting and northing coordinates matrices of the Z_image. '''

       return self.data.easting_image, self.data.northing_image

   #---------------------------------------------------------------------------#
   # DataSet Geopositioning                                                    #
   #---------------------------------------------------------------------------#
   def to_kml(self, plottype, cmapname, kmlfilename, creversed=False, picturefilename="image.png", cmmin=None, cmmax=None, interpolation='bilinear', dpi=100):
      '''
      Plot in 2D dimensions the cartography representation to export in google earth.

      Parameters :

      :plottype: plotting type, '2D-SURFACE', '2D-CONTOUR', ...xyz

      :cmapname: name of the color map used.

      :kmlfilename: name of the kml file to create

      :creversed: True to add '_r' at the cmname to reverse the color map

      :picturefilename: name of the picture file to save, None if no file to save.

      :cmmin: minimal value to display in the color map range.

      :cmmax: maximal value to display in the color map range.

      :interpolation: interpolation mode to display DataSet Image ('bilinear', 'nearest', 'bicubic'), 'bilinear' by default.

      :cmapdisplay: True to display color map bar, False to hide the color map bar.

      :axisdisplay: True to display axis and labels, False to hide axis and labels

      :dpi: 'dot per inch' definition of the picture file if filename != None

      Returns:

      :success: True if success, False if not.

      '''
      # calculation of the 4 points utm coordinates
      success, [blcorner, brcorner, urcorner, ulcorner] = self.getquadcoords()

      if (success == True):
         # utm to wgs84 conversion
         blcorner_wgs84_lat, blcorner_wgs84_lon = geopos.utm_to_wgs84(blcorner.utm_easting, blcorner.utm_northing, self.georef.utm_zonenumber, self.georef.utm_zoneletter)
         brcorner_wgs84_lat, brcorner_wgs84_lon = geopos.utm_to_wgs84(brcorner.utm_easting, brcorner.utm_northing, self.georef.utm_zonenumber, self.georef.utm_zoneletter)
         urcorner_wgs84_lat, urcorner_wgs84_lon = geopos.utm_to_wgs84(urcorner.utm_easting, urcorner.utm_northing, self.georef.utm_zonenumber, self.georef.utm_zoneletter)
         ulcorner_wgs84_lat, ulcorner_wgs84_lon = geopos.utm_to_wgs84(ulcorner.utm_easting, ulcorner.utm_northing, self.georef.utm_zonenumber, self.georef.utm_zoneletter)

         quadcoords = [(blcorner_wgs84_lon, blcorner_wgs84_lat), (brcorner_wgs84_lon, brcorner_wgs84_lat), (urcorner_wgs84_lon, urcorner_wgs84_lat), (ulcorner_wgs84_lon, ulcorner_wgs84_lat)]

         # creation of the picture file to overlay
         self.plot(plottype, cmapname, creversed, fig=None, filename=picturefilename, cmmin=cmmin, cmmax=cmmax, interpolation=interpolation, cmapdisplay=False, axisdisplay=False, dpi=dpi, transparent=True)

         # creation of the kml file
         kml.picture_to_kml(picturefilename, quadcoords, kmlfilename)

      return success

   def to_raster(self, plottype, cmapname, picturefilename, creversed=False, cmmin=None, cmmax=None, interpolation='bilinear', dpi=100):
      '''
      Plot in 2D dimensions the cartography representation with the world file associated, to using in a SIG application.

      Parameters:

      :plottype: plotting type, '2D-SURFACE', '2D-CONTOUR', ...xyz

      :cmapname: name of the color map used.

      :picturefilename: name of the picture file to save (.jpg, .jpeg, .tif, .tiff, .png) , None if no file to save.

      :creversed: True to add '_r' at the cmname to reverse the color map

      :cmmin: minimal value to display in the color map range.

      :cmmax: maximal value to display in the color map range.

      :interpolation: interpolation mode to display DataSet Image ('bilinear', 'nearest', 'bicubic'), 'bilinear' by default.

      :dpi: 'dot per inch' definition of the picture file

      Returns:

      :success: True if success, False if not.

      '''
      # calculation of the 4 points utm coordinates
      success, [blcorner, brcorner, urcorner, ulcorner] = self.getquadcoords()

      if (success == True):
         # tests if picture format available for raster
         success = raster.israsterformat(picturefilename)

         if (success == True):
            quadcoords = [(blcorner.utm_easting, blcorner.utm_northing), (brcorner.utm_easting, brcorner.utm_northing), (urcorner.utm_easting, urcorner.utm_northing), (ulcorner.utm_easting, ulcorner.utm_northing)]

            # creation of the picture file to overlay
            self.plot(plottype, cmapname, creversed, fig=None, filename=picturefilename, cmmin=cmmin, cmmax=cmmax, interpolation=interpolation, cmapdisplay=False, axisdisplay=False, dpi=dpi, transparent=True)

            # creation of the world file
            success = raster.picture_to_worldfile(picturefilename, quadcoords)

      return success

   def setgeoref(self, refsystem, points_list, utm_zoneletter=None, utm_zonenumber=None, valfilt=False):
      ''' Georeferencing dataset using 2-D linear interpolation.

      Dataset is georeferenced using a list of Ground Control Points (GCPs).
      The geographic positions are linearly interpolated in 2-D at the dataset position.

      As no exrapolatio is available yet, there must GCPs that spatially includes
      the dataset positions (typically grid nodes).
      
      Parameters
      ----------
      refsystem : str or None
          Geographic reference system ('UTM', 'WGS84', ...).

      points_list : list
          List of GCPs points. ex:
          [[num1, lat1, lon1, x1, y1], ..., [numN, latN, lonN, xN, yN]].

      utm_zoneletter : str or None
        UTM zone letter if `refsystem` is 'UTM'.

      utm_zonenumber : int or None
          UTM zone number if `refsystem` is 'UTM'.

      valfilt : bool
          If True, the ungridded dataset value (class:`~values`) are used instead
          of the gridded (class:`~z_images`).
          Then, the georeferenced coordinates will be stored in :obj:`eatsing` and :obj:`northing`
          instead of :obj:`easting_image` and :obj:`northing_image`.

      Returns
      -------
      error : {0, -1, -2}
          Error code.
          0 if no error occured.
          -1 if there are not enough points.
          -2 if an error occured during georeferenincg,
          probably the dataset are unconsistent with the GCPs area.

      Georeferenced dataset object

      '''

      return gengeopositioning.setgeoref(self, refsystem, points_list,
                                         utm_zoneletter=utm_zoneletter,
                                         utm_zonenumber=utm_zonenumber,
                                         valfilt=valfilt)

   def getquadcoords(self):
      '''
      Calculates the utm coordinates of the DataSet Image corners.

      Returns:

      :success: True if coordinates getted, False if not

      :bottomleft: utm coordinates of the bottom left corner

      :bottomright: utm coordinates of the bottom right corner

      :upright: utm coordinates of the up right corner

      :upleft: utm coordinates of the up left corner

      '''
      bottomleft = None
      bottomright = None
      upright = None
      upleft = None
      if (self.georef.active == True):
         bottomleft = GeoRefPoint()
         bottomright = GeoRefPoint()
         upright = GeoRefPoint()
         upleft = GeoRefPoint()
         bottomleft.utm_easting, bottomleft.utm_northing = self.data.easting_image[0][0], self.data.northing_image[0][0]
         bottomright.utm_easting, bottomright.utm_northing = self.data.easting_image[0][-1], self.data.northing_image[0][-1]
         upleft.utm_easting, upleft.utm_northing = self.data.easting_image[-1][0], self.data.northing_image[-1][0]
         upright.utm_easting, upright.utm_northing = self.data.easting_image[-1][-1], self.data.northing_image[-1][-1]

      return self.georef.active, [bottomleft, bottomright, upright, upleft]

   #---------------------------------------------------------------------------#
   # DataSet General Processing                                                #
   #---------------------------------------------------------------------------#
   def threshold(self, setmin=None, setmax=None, setmed=False, setnan=False, valfilt=False):
      '''
      Threshold a dataset in the given interval.

      Returns the thresholded :func:`~geophpy.dataset.DataSet` object.

      Parameters
      ----------
      setmin : float
          Minimal interval value.
          All values lower than ``setmin`` will be replaced by ``setmin``
          (if both ``setmed`` and ``setnan`` are False).

      setmax : float
          Maximal interval value.
          All values lower than ``setmax`` will be replaced by ``setmax``
          (if both ``setmed`` and ``setnan`` are False).

      setmed : bool
          If set to True, out of range values are replaced by the profile's median.

      setnan : bool
          If set to True, out of range values are replaced by NaNs

      valfilt : bool
          If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
          are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

      Note
      ----
      If both ``setnan`` and ``setmed`` are True at the same time, ``setnan`` prevails.

      '''
      return genproc.threshold(self, setmin=setmin, setmax=setmax, setmed=setmed, setnan=setnan, valfilt=valfilt)

   def peakfilt(self, method='hampel', halfwidth=5, threshold=3, mode='relative', setnan=False, valfilt=False):
       '''
       Eliminate peaks from the dataset.

       Returns the de-peaked :func:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------

       method : str {'median', 'hampel'}
           Type of the ``decision-theoric filter`` used to determine outliers.

       halfwidth : scalar
           Filter half-width.

       threshold : scalar (positive)
           Filter threshold parameter.
           If t=0 and method='hampel', it is equal to a ``standard median filter``.

       mode : str {'relative', 'absolute'}
           Median filter mode. If 'relative', the threshold is a percentage of the local
           median value. If 'absolute', the threshold is a value.

       setnan : bool
           If True, the outliers are replaced by nan instead of the local median.

       valfilt : bool
           If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

       '''

       return genproc.peakfilt(self, method=method, halfwidth=halfwidth,
                                      threshold=threshold,mode=mode, setnan=setnan, valfilt=valfilt)

   def medianfilt(self, nx=3, ny=3, percent=0, gap=0, valfilt=False):
       '''
       Apply a median filter (*decision-theoretic* or *standard*) to the dataset.

       Returns the filtered :func:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------
       nx : int
           Size, in number of sample, of the filer in the x-direction.

       ny : int
           Size, in number of sample, of the filter in the y-direction.

       percent : float
           Threshold deviation (in percents) to the local median value (for absolute field measurements).

       gap : float
           Threshold deviation (in raw units) to the median value (for relative anomaly measurements).

       valfilt : bool
           If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

       '''
       
       return genproc.medianfilt(self, nx=nx, ny=ny, percent=percent, gap=gap, valfilt=valfilt)

   def festoonfilt(self, method='Crosscorr', shift=0, corrmin=0.4, uniformshift=False,
                   setmin=None, setmax=None, valfilt=False):
       '''
       Filters festoon-like artefacts out of in the dataset.

       Returns the destaggered :func:`~geophpy.dataset.DataSet` object
       and the shift used for each profile.

       Parameters
       ----------
       method : str, {'Crosscorr', 'Pearson', 'Spearman' or 'Kendall'} (from :func:`~geophpy.dataset.festooncorrelation_getlist`)
           Correlation method to use to compute the correlation coefficient in the correlation map.

       shift : scalar or array of float
           Shift value (in pixels) to apply to the dataset profile.
           If shit=0, the shift will be determined for each profile by correlation with neighbours.
           If shift is a vector each value in shift will be applied to its corresponding odd profile.
           In that case shift must have the same size as the number of odd profiles.

       corrmin : scalar in the range [0-1]
           Minimum correlation coefficient value to allow shifting.

       uniformshift : bool
           If True, the shift is uniform on the map. If False the shift depends on each profile.

       setmin : float
           Data values lower than ``setmin`` are ignored.

       setmax : float
           Data values higher than ``setmax`` are ignored.

       valfilt : bool
           If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

       Returns
       -------
       shift : array of float
           Shift values used to destagger the dataset (unmodified if provided as an input parameter).

       See Also
       --------
       correlmap, correlshift

       Notes
       -----
       The festoon-like artefacts are filtered based on the correlation between
       neighboring profiles.

       For each odd profile index in the dataset, the correlation with its
       neighboring profile is calculated using the provided ``correlation method``.
       Then, the profile is shifted from a sample and the correlation is computed
       anew and so forth to build a ``correlation map`` fo revery possible shift.
       For each profile, the shift with the maximum correlation coefficient is
       chosen as the ``best shift`` and used to destagger the dataset.
       It the shift is set to be uniform on the map, the correlation map is
       summed up and the shit correspoding to the global maximum correlation
       coefficient is used for each odd profile.

       Alternatively, if a custom ``set of shift`` is provided, it will be used to
       destagger the dataset. It must have the same size as the number of odd profile
       in the dataset.

       Example
       -------

       >>> dataset.festoonfilt(method='Crosscorr', shift=0, corrmin=0.6, uniformshift=False)

       '''

       return genproc.festoonfilt(self, setmin=None, setmax=None, method=method, shift=shift,
                                        corrmin=corrmin, uniformshift=uniformshift, valfilt=valfilt)

   def correlmap(self, method='Crosscor'):
       ''' Profile-to-profile correlation map.

       Each even profile in the dataset is incrementally shifted and
       the correlation coefficient is computed against the (standardized) mean
       of the two neighbouring profiles for each shift value.

       Profiles are considered to be vertical and the shift is performed along
       the profile direction (y-direction).
       For a dataset of size ny*nx , the correlation map size is then 2*ny*nx
       (shift may vary from -ymax to +ymax).

       Parameters
       ----------
       method : str, {'Crosscor', 'Pearson', 'Spearman', 'Kendall'}
           Correlation method use.

       Returns
       -------
       cormap : 2-D array_like
           Profile-to-profile correlation map.

       pva1 : 2-D array_like
           Correlation weight map.

       '''

       return genproc.correlmap(self, method)

   def zeromeanprofile(self, setvar='median', setmin=None, setmax=None, valfilt=False):
       r'''
       Subtract the mean (or median) of each profile in the dataset.

       Returns the zero-mean (or zero-median) :func:`~geophpy.dataset.DataSet` object.
      
       Parameters
       ----------
       setvar: str, {'mean', 'median'}
           Profile's statistical property be subtracted from each profile.

       setmin: float
           While computing the mean, do not take into account data values lower than *setmin*.

       setmax: float
           While computing the mean, do not take into account data values greater than *setmax*.

       valfilt : bool
           If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

       See Also
       --------
       destripecon, destripecub

       Notes
       -----
       For each profile in the dataset, the mean (or median depending on
       ``setvar``) is calculated and subtracted from the profile.

       This is equivalent to the :func:`~geophpy.dataset.DataSet.destripecon` method in
       configuration ``mono sensor`` using the ``additive`` destriping ``method`` and a
       ``number of profile`` for the calculation equals to ``zero``.

       Examples
       --------
       >>> dataset.zeromeanprofile(setvar='median')
           equivalent to
       >>> dataset.destripecon(Nprof=0, method='additive', config='mono', reference='median')
       '''

       return genproc.zeromeanprofile(self, setvar=setvar, setmin=setmin, setmax=setmax, valfilt=valfilt)

   def destripecon(self, Nprof='all', setmin=None, setmax=None, method='additive', reference='mean', config='mono', valfilt=False):
       '''
       Destriping dataset using profiles' statistical moments (Moment Matching method).

       Moment Matching method: the statistical moments (mean and standard deviation)
       of each profile in the dataset are computed and matched to reference values.

       Parameters
       ----------
       Nprof : int or str ('all')
           Number of neighboring profiles used to compute the the reference values.
           Set to ``'all'`` by default) to compute the mean over the whole dataset. 
           If set to ``0``, it is the zero-mean (or zero-median) traverse filter.

       setmin : float or None
           While computing the mean, do not take into account data values lower than ``setmin``.
           If ``None``, all data are considered.

       setmax : float or None
           While computing the mean, do not take into account data values greater than ``setmax``.
           If ``None``, all data are considered.

       method : str {'additive','multiplicative'}
           Destriping methode.
           If set to ``'additive'`` (default), destriping is done additively.  
           If set to ``'multiplicative'``, it is done multiplicatively.

       reference : str {'mean' 'median'}
           References used for destriping.
           If set to ``'mean'`` (default), destriping is done using mean and standard deviation.
           If set to ``'median'``, destriping is done using median and interquartile range.

       config : str {'mono','multi'}
           Sensors configuration.
           If set to ``'mono'`` (default), destriping is done using only offset matching (mean or median). 
           If set to ``'multi'``, destriping is done using both offset and gain (mean and standard deviation or median and interquartile range).

       valfilt : bool
           If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

       '''

       return genproc.destripecon(self, Nprof=Nprof, setmin=setmin, setmax=setmax, method=method, reference=reference, config=config, valfilt=valfilt)

   def destripecub(self, Nprof=0, setmin=None, setmax=None, Ndeg=3, valfilt=False):
      '''
      To destripe a DataSet Object by a cubic curvilinear regression (chi squared)

      Parameters:

      :dataset: DataSet Object to be destriped

      :Nprof: number of profiles over which to compute the polynomial reference ; if set to 0 (default), compute the mean over the whole data

      :setmin: while fitting the polynomial curve, do not take into account data values lower than setmin

      :setmax: while fitting the polynomail curve, do not take into account data values greater than setmax

      :Ndeg: polynomial degree of the curve to fit

      :valfilt: If True, the dataset *values* are filtered instead of the dataset *z_image*.

      See Also
      --------
      destripecon, zeromeanprofile
      '''

      return genproc.destripecub(self, Nprof=Nprof, setmin=setmin, setmax=setmax, Ndeg=Ndeg, valfilt=valfilt)

   def detrend(self, order=1, setmin=None, setmax=None, valfilt=False):
       '''
       Remove trend from dataset's profiles.

       Subtract a polynomial fit for each profile in the dataset and return the
       detrendend :func:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------
       order : int
           Degree for the fitting polynomial.
           
       setmin: float
           While computing the fit, do not take into account data values lower than *setmin*.

       setmax: float
           While computing the fit, do not take into account data values greater than *setmax*.

       valfilt : bool
           If set to True, the ungridded :func:`~geophpy.dataset.DataSet.data.values`
           are filtered instead of the gridded :func:`~geophpy.dataset.DataSet.data.z_image`.

       See Also
       --------
       destripecon, zeromeanprofile, regtrend
       '''

       ### TODO
       ## Implement moving window detrending for multitrend on a profile
       ## Implement jumpdiscontinuities detrending
       ###

       return genproc.detrend(self, order=order, setmin=setmin, setmax=setmax, valfilt=valfilt)


   def regtrend(self, nx=3, ny=3, method='relative', component='local', valfilt=False):
      '''
      To filter a DataSet Object from its regional trend

      Parameters:

      :dataset: DataSet Object to be filtered

      :nx: filter size in x coordinate

      :ny: filter size in y coordinate

      :method: set to "relative" to filter by relative value (resistivity) or to "absolute" to filter by absolute value (magnetic field)

      :component: set to "local" to keep the local variations or to "regional" to keep regional variations

      :valfilt: if set to True, then filters data.values instead of data.zimage

      '''
      return genproc.regtrend(self, nx=nx, ny=ny, method=method, component=component, valfilt=valfilt)

   def wallisfilt(self, nx=11, ny=11, targmean=125, targstdev=50, setgain=8,
                  limitstdev=25, edgefactor=0.1, valfilt=False):
      r'''
      Apply the Wallis contrast enhancement filter to the dataset.

      Returns the contrast-enhanced :func:`~geophpy.dataset.DataSet` object.

      Parameters
      ----------
      nx : int
          filter window size in x-direction
    
      ny : int
          filter window size in y-direction

      targmean : float
          The target mean brigthness level (:math:`m_d`)

      targstdev : float
          The target standard deviation (:math:`\sigma_d`)

      setgain : float
          Amplification factor for contrast (:math:`A`)

      limitstdev : float
          Limitation on the window standard deviation to prevent too high gain value if data are dispersed

      edgefactor : float in the range of [0,1]
          Brightness forcing factor (:math:`\alpha`), controls ratio of edge to background intensities.

      valfilt : bool
          If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
          are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

      Notes
      -----

      The Wallis filter is a locally adaptative contrast enhancement filter
      based on the local statistical properties of sub-windows in the image.
      It adjusts brightness values (grayscale image) in the local window so that
      the local mean and standard deviation match target values.

      The Wallis operator is defined as [#]_:

      .. math::
         \frac{A \sigma_d}{A \sigma_{(x, y)} + \sigma_d} [f_{(x, y)} - m_{(x, y)}] + \alpha m_d + (1 - \alpha)m_{(x, y)}

      where: :math:`A` is the amplification factor for contrast;
      :math:`\sigma_d` is the target standard deviation;
      :math:`\sigma_{(x, y)}` is the standard deviation in the current window;
      :math:`f_{(x, y)}` is the center pixel of the current window;
      :math:`m_{(x, y)}` is the mean of the current window;
      :math:`\alpha` is the edge factor (controlling portion of the observed mean, and brightness locally to reduce or increase the total range) and
      :math:`m_d` is the target mean.

      As the Wallis filter is design for grayscale image, the data are
      internally converted to brightness level before applying the filter.
      The conversion is based on the minimum and maximum value in the dataset
      and uses 256 levels (from 0 to 255).

      References
      ----------

      .. [#] Scollar I., Tabbagh A., Hesse A. and Herzog I. 1990.
         Archaeological Prospecting and Remote Sensing (Topics in Remote Sensing 2).
         647p, chapter 4.5 p174.
         Cambridge University Press.

      Examples
      --------
      >>> dataset.wallisfilt()
      >>> dataset.wallisfilt(nx=21, ny=21, targmean=125, targstdev=50)
      '''

      return genproc.wallisfilt(self, nx=nx, ny=ny, targmean=targmean, targstdev=targstdev, setgain=setgain, limitstdev=limitstdev, edgefactor=edgefactor, valfilt=valfilt)

   def ploughfilt(self, apod=0, azimuth=0, cutoff=100, width=2, valfilt=False):
      r'''
      Apply a directionnal ("anti-ploughing") filter to the dataset.

      Returns the filtered :meth:`~geophpy.dataset.DataSet` object.

      Parameters
      ----------

      apod : float
          Apodization factor in percent [0,1].

      azimuth : scalar
          Filter azimuth in degree.

      cutoff : scalar
          Cutoff spatial frequency (in number of sample).

      width : int
          Filter width parameter.

      valfilt : bool
          If set to True, the :func:`~geophpy.dataset.DataSet.data.values`
          are filtered instead of the :func:`~geophpy.dataset.DataSet.data.z_image`.

      Notes
      -----

      The filter used is a combination of a classic gaussian low-pass filter of order 2 with a directional filter.
      This gaussian low-pass directional filter is defined as [#]_:

      .. math::
         \mathcal{F}(\rho, \theta, f_c) = e^{-(\rho / f_c)^2} \cdot ( 1-e^{-r^2 / \tan(\theta - \theta_0)^n} )

      where: :math:`\rho` and :math:`\theta` are the current point polar coordinates; 
      :math:`f_c` is the gaussian low-pass filter cutoff frequency; 
      :math:`\theta_0` is the directional filter's azimuth and 
      :math:`n` is the parameter that controls the filter width.

      References
      ----------

      .. [#] Tabbagh J. 2001.
         Filtre directionel permettant d'eliminer les anomalies crees par le labour,
         in "Filtering, Optimisation and Modelling of Geophysical Data in Archaeological Prospecting",
         Fondazione Ing. Carlo Maurillo Lerici, Politecnico di Milano, M. Cucarzi and P. Conti (eds.),
         Roma 2001, 202p, p161-166.

      Examples
      --------
      >>> dataset.ploughfilt()
      >>> dataset.ploughfilt(apod=0, azimuth=30, cutoff=100, width=2)
      >>> dataset.ploughfilt(azimuth=45, cutoff=None)

      '''

      return genproc.ploughfilt(self, apod=apod, azimuth=azimuth, cutoff=cutoff, width=width, valfilt=valfilt)

   #---------------------------------------------------------------------------#
   # DataSet Magnetism Processing                                              #
   #---------------------------------------------------------------------------#
   def logtransform(self, multfactor=1, setnan=True, valfilt=False):
       r'''

       Apply a logarihtmic transformation to the dataset.

       The logarihtmic transformation is a contrast enhancement filter that
       enhances information at low-amplitude values while preserving the
       relative amplitude information.

       Returns the transformed :meth:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------
       multfactor : float
           Multiplying factor to apply to the data to increase/decrease the number of data that falls into the condition ]-1,1[.

       setnan : bool,
          If True, the data value between ]-1,1[ will be replaced by nans. 
          If False, they will be replaced by zero.

       valfilt : bool,
          If True, then filters :attr:`~geophpy.dataset.Data.values` instead of :attr:`~geophpy.dataset.Data.data.z_image`

       Notes
       -----

       The logarihtmic transformation is defined as [#]_:

       .. math::
          \mathcal{F}\{f\} =
             \left\{
             \begin{array}{ccc}
                -\log_{10} (-f) & for & f <-1 \\
                 \log_{10} (f) & for & f >1 \\
                     0         & for & -1< f >1 \\
             \end{array}
             \right.

       where: :math:`f` is the original data.

       References
       ----------

       .. [#] Morris B., Pozza M., Boyce J. and Leblanc G. 2001.
          Enhancement of magnetic data by logarithmic transformation.
          The Leading Edge, vol. 20, no. 8, p882-885.

       '''

       return magproc.logtransform(self, multfactor=multfactor, setnan=setnan, valfilt=valfilt)

   def polereduction(self, apod=0, inclination=65, declination=0, azimuth=0,
                  magazimuth=None, incl_magn=None, decl_magn=None):
       r'''
       Reduction to the pole.

       The reduction to the pole is a phase transformation in the spectral domain
       applied to the **total magnetic field** to computes the
       "anomaly that would be measured at the north magnetic pole,
       where induced magnetization and ambient field both would be directed
       vertically down." [#]_

       Returns the transformed :meth:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------

       apod : float
           Apodization factor, to limit Gibbs phenomenon at jump discontinuities.

       inclination : float
           Ambient magnetic field inclination (:math:`I`) in degrees
           positive below horizontal.

       declination : float
           Ambient magnetic field declination (:math:`D`) in degrees
           positive east of geographic (true) north.

       azimuth : float
           Azimuth of the survey **x-axis** in degrees positive east of north
           (:math:`\theta`, the angle between the survey profile direction and the geographic north).
           The `magnetic azimuth` (:math:`\phi`) is computed from the ``declination`` (:math:`D`)
           and the azimuth as :math:`\phi= D - \theta`.

       magazimuth :  float
           `Magnetic azimuth` survey **x-axis** in degrees positive east of north
           (:math:`\phi`, the angle between the survey profile direction and the magnetic north).
           ``None`` by default. If a value is given, the ``declination`` is ignored and the magnetic azimuth will derectly be used.

       incl_magn, decl_magn : float, optional
           The source remanent magnetization inclination and declination in degrees.
           By default they are set to ``None``, the remanent magnetization is neglected.

       Notes
       -----

       If the magnetization and ambient field are not vertical, a uniform
       magnetic source will produce a skewed anomaly. 
       The reduction to the pole aims to eliminate this effect by transforming
       the "measured **total field** anomaly into the vertical component of the
       field caused by the same source distribution magnetized in the vertical direction".

       This transformation is given in the spectral domain by:

       .. math::
          \mathcal{F}_{RTP} = \mathcal{F}_{TF} \cdot \mathcal{F}

       where :math:`\mathcal{F}_{TF}` is the Fourier Transform of measured `total field` anomaly and :math:`\mathcal{F}` is defined as:

       .. math::
          \mathcal{F}_{m,f}\{k_x, k_x\} = \frac{|k|^2}{
              a_1 k_x^2
              + a_2 k_y^2
              + a_3 k_x k_y
              + i |k| (b1 k_x + b2 k_y)}, |k| \ne 0

       with

       .. math::
          a_1 &= m_z f_z - m_x f_x, \\
          a_2 &= m_z f_z - m_y f_y, \\
          a_3 &= -m_y f_x - m_x f_y, \\
          b_1 &= m_x f_z + m_z f_x, \\
          b_2 &= m_y f_z + m_z f_y, \\

       where :math:`m=(m_x, m_y, m_z)` is the unit-vector in the direction of the magnetization of the source;
       :math:`f = (f_x, f_y, f_z)` is the unit-vector in the direction of the ambiant field;
       :math:`|k| = \sqrt{k_x^2 + k_y^2}` is the radial wavenumber and
       :math:`k_x` and :math:`k_y` are the wavenumber in the x and y-diection respectively.


       References
       ----------

       .. [#] Blakely R. J. 1996. 
          Potential Theory in Gravity and Magnetic Applications. 
          Chapter 12.3.1, p330. 
          Cambridge University Press.

       '''

       return magproc.polereduction(self, apod=apod, inclination=inclination, declination=declination,
                                          azimuth=azimuth, magazimuth=magazimuth,
                                          incl_magn=incl_magn, decl_magn=decl_magn)

   def continuation(self, apod=0, distance=2, continuationflag=True, totalfieldconversionflag=False, separation=0.7):
       r'''
       Upward or downwad continuation of the magnetic field.

       The continuation computes the data that would be measured at an upper
       (`upward continuation`) or lower survey altitude
       (`downward continuation`). The computation is done in the spectral
       (frequency) domain using Fast Fourier Transform.

       Returns the continued :meth:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------
       apod : float
           Apodization factor (in %), to limit Gibbs phenomenon at jump discontinuities.

       distance : float
           Continuation distance. Positive for an `upward continuation` (above ground level, away from the source) and
           negative for a `downward continuation` (under ground level, toward the source).

       totalfieldconversionflag: bool,
           If True, the data are considered as gradient data (Total-field gradient or Fluxgate)
           and will be converted to total-field data after the continuation using the provided separation.

       separation :folat
           Sensor separation for the conversion to Total-field data.

       Notes
       -----
       
       Assuming that all the magnetic sources are located below the observation surface,
       the continuation at a new observation altitude :math:`z` of a survey
       acquired at an original altitude :math:`z_0` is given in the spectral
       domain by [#]_:

       .. math::

          \mathcal{F}_{\Delta z,k} = \mathcal{F}_{TF} \cdot e^{-\Delta z |k|}

       where :math:`\mathcal{F}_{TF}` is the Fourier Transform of the measured data at the original altitude of observation :math:`z_0`; 
       :math:`\mathcal{F}_{\Delta z,k}` is the Fourier Transform of the anomaly at the new altitude of observation :math:`z = z_0 - \Delta z`; 
       :math:`\Delta z = z_0 - z` is the altitude increase between the original and new altitude of observation and  
       :math:`|k| = \sqrt{k_x^2 + k_y^2}` is the radial wavenumber where :math:`k_x` and :math:`k_y` are the wavenumber in the x and y-direction respectively.

       The given  altitude increase (:math:`\Delta z`) is an algebraic value:

       * If :math:`\Delta z>0`, the new altitude of observation is above the original altitude: the operation is an `upward continuation`; 
       * if :math:`\Delta z<0`, the new altitude of observation is below the original altitude: the operation is a `downward continuation`.

       The `upward continuation` attenuates anomalies with respect to the wavelength in way that accentuates anomalies caused by deep sources and  attenuates at the anomalies caused by shallow sources. 
       It is hence a smoothing operator.

       The `downward continuation` accentuates the shallowest components. It reduces spread of anomalies and corrects anomalies coalescences. 
       It is usefull to discriminates the number of body source at the origin of a one big anomaly. 
       It is an unsmoothing operator that is instable as small changes in the data can cause large and unrealistic variations so it is to be used with caution. 
       Low-pass filtering before the `downward continuation` can be a solution to increase the filter stability.

       References
       ----------

       .. [#] Blakely R. J. 1996. 
          Potential Theory in Gravity and Magnetic Applications. 
          Chapter 12.1, p313-320. 
          Cambridge University Press.

       '''

       return magproc.continuation(self, apod=apod, distance=distance, totalfieldconversionflag=totalfieldconversionflag, separation=separation)

   def eulerdeconvolution(self, apod=0, structind=None, windows=None, xstep=None, ystep=None):
       r'''
       Classic Euler deconvolution.

       Euler deconvolution is a method to estimate magnetic sources depth based on Euler's homogeneity relation.

       Parameters
       ----------
       apod : float
           Apodization factor, to limit Gibbs phenomenon at jump discontinuities.

       structind : int {1, 2, 3, None}
           The Structural Index to used for the Euler deconvolution.
           If None, it will be estimated by Least-square regression simultenaously
           with the source position and depth for each dataset sub-window.

       windows : list or None
           The list containing the satial extent of each sub-window to be considered
           for the deconvolution: 
           [[xmin1, xmax1, ymin1, ymax1],...,[xmink, xmaxk, ymink, ymaxk]].
           If None, a 2-D sliding window od size *xstep x ystep* will be created
           and used for the deconvolution.

       xstep : int
           Size, in number of sample, of the sub-windows in the x-direction.
           Used only if windows is None.
           If Only xstep is specified, a square window is used.

       ystep : int
           Size, in number of sample, of the sub-windows in the y-direction.
           Used only if windows is None.
           If Only ystep is specified, a square window is used.

       Returns
       -------
       out : list
           The list containing for each sub-window,
           the estimated source x and y position and
           depth, the structural index , the corresponding residuals
           and the correspondig sub-window spatial extend.

       Note
       ----
       [#]_

       References
       ----------
      
        .. [#] Reid A. B., Allsop J. M., Granser H., Millett A. J. and Somerton I. W. 1990. 
           Magnetic interpretation in three dimensions using Euler deconvolution. 
           Geophysics, vol. 55, no. 1, p80-91.

       '''

       return magproc.eulerdeconvolution(self, apod=apod, structind=structind, windows=windows, xstep=xstep, ystep=ystep)

   def analyticsignal(self, apod=0):
       r'''
       Conversion from potential field to *analytic signal*.

       Parameters
       ----------
       apod : float
           Apodization factor, to limit Gibbs phenomenon at jump discontinuities.

       Notes
       -----
       The amplitude of the *analytical signal* (or the *amplitude of the total gradient*)
       of a potential field :math:`T` is defined as [#]_:

       .. math::

          |A(x, y, z)| = \sqrt{ \left( \frac{\partial T}{\partial x} \right)^2
                    + \left( \frac{\partial T}{\partial y} \right)^2
                    + \left( \frac{\partial T}{\partial z} \right)^2 }

       The directional derivative are computed in the spectral domain using [#]_:

       .. math::

          \mathcal{F} \left[ \frac{\partial^2 T}{\partial x^2} \right] = (ik_x)^2 \mathcal{F} \left[ T \right], 
          \mathcal{F} \left[ \frac{\partial^2 T}{\partial y^2} \right] = (ik_y)^2 \mathcal{F} \left[ T \right], 
          \mathcal{F} \left[ \frac{\partial^2 T}{\partial z^2} \right] = |k|^2 \mathcal{F} \left[ T \right].

       and transformed back in the spatial domain for the total gradient amplitude calculation.

       References
       ----------

       .. [#] Blakely R. J. 1996. 
          Potential Theory in Gravity and Magnetic Applications. 
          Chapter 12.1, p313-320. 
          Cambridge University Press.

       .. [#] Roest Walter R. , Verhoef Jacob and Pilkington Mark 1992. 
          Magnetic interpretation using the 3-D analytic signal. 
          Geophysics, vol. 57, no. 1, p116-125.

       '''

       return magproc.analyticsignal(self, apod=apod)

   def magconfigconversion(self, fromconfig, toconfig, apod=0,
                           FromBottomSensorAlt=0.3, FromTopSensorAlt=1.0, ToBottomSensorAlt=0.3, ToTopSensorAlt=1.0,
                           inclination=65, declination=0, azimuth=0, magazimuth=None):
       r'''
       Conversion between the different magnetic survey sensor's configurations.

       Returns the transformed :meth:`~geophpy.dataset.DataSet` object.

       Parameters
       ----------
       fromconfig : str {"TotalField"|"TotalFieldGradient"|"Fluxgate"}, from sensorconfig_getlist()
           Initial sensor's configuration from which to convert de data.

       toconfig : str {"TotalField"|"TotalFieldGradient"|"Fluxgate"}, from sensorconfig_getlist()
           Final sensor's configuration to which to convert de data.

       apod : float
           Apodization factor, to limit Gibbs phenomenon at jump discontinuities.

       FromBottomSensorAlt : float
          Bottom sensor altidue of the initial sensor's configuration.

       FromTopSensorAlt : float
          Top sensor altidue of the initial sensor's configuration.

       ToBottomSensorAlt : float
          Bottom sensor altidue of the final sensor's configuration.

       ToTopSensorAlt : float
          Top sensor altidue of the final sensor's configuration.

       inclination : float
           Ambient magnetic field inclination (:math:`I`) in degrees
           positive below horizontal.

       declination : float
           Ambient magnetic field declination (:math:`D`) in degrees
           positive east of geographic (true) north.

       azimuth : float
           Azimuth of the survey **x-axis** in degrees positive east of north
           (:math:`\theta`, the angle between the survey profile direction and the geographic north).
           The `magnetic azimuth` (:math:`\phi`) is computed from the ``declination`` (:math:`D`)
           and the azimuth as :math:`\phi= D - \theta`.

       magazimuth :  float
           `Magnetic azimuth` survey **x-axis** in degrees positive east of north
           (:math:`\phi`, the angle between the survey profile direction and the magnetic north).
           ``None`` by default. If a value is given, the ``declination`` is ignored and the magnetic azimuth will derectly be used.

       Notes
       -----
       as [#]_:

       References
       ----------

       .. [#] Tabbagh A., Desvignes G. and Dabas M. 1997. 
          Processing of Z Gradiometer Magnetic data using Linear Transforms and Analytical Signal. 
          Archaelogical Prospection, vol. 4, issue 1, p1-13. 

       '''

       return magproc.magconfigconversion(self, fromconfig, toconfig, apod=apod,
                                                FromBottomSensorAlt=FromBottomSensorAlt, FromTopSensorAlt=FromTopSensorAlt,
                                                ToBottomSensorAlt=ToBottomSensorAlt, ToTopSensorAlt=ToTopSensorAlt,
                                                inclination=inclination, declination=declination, azimuth=azimuth, magazimuth=magazimuth)

   def susceptibility(self, prosptech, apod=0, downsensoraltitude = 0.3, upsensoraltitude = 1.0, calculationdepth=.0, stratumthickness=1.0, inclineangle = 65, alphaangle = 0):
      '''
      Calcultation of an equivalent stratum of magnetic susceptibility

      Parameters :

      :prosptech: Prospection technical

      :apod: apodization factor, to limit side effects

      :downsensoraltitude: Altitude of the down magnetic sensor

      :upsensoraltitude: Altitude of the upper magnetic sensor

      :calculationdepth: Depth(m) to do the calculation

      :stratumthickness: Thickness of the equivalent stratim

      :inclineangle: magnetic field incline

      :alphaangle: magnetic field alpha angle
      '''
      return magproc.susceptibility(self, prosptech, apod, downsensoraltitude, upsensoraltitude, calculationdepth, stratumthickness, inclineangle, alphaangle)


#===========================================================================#


#---------------------------------------------------------------------------#
# General DataSet Environment functions                                     #
#---------------------------------------------------------------------------#
format_chooser = {
   ".dat" : "ascii",
   ".txt" : "ascii",
   ".xyz" : "ascii",
   ".csv" : "ascii",
   ".nc"  : "netcdf",
   ".cdf" : "netcdf",
   ".pga" : "wumap",
   ".grd" : "surfer",
   ".mat" : "matrix",
   ".app" : "profile",
   ".rt"  : "electric",
}


def getlinesfrom_file(filename, fileformat=None, delimiter='\t', skipinitialspace=True, skiprowsnb=0, rowsnb=1):
   '''
   Reads lines in a file.

   Parameters :

   :fileformat: file format

   :filename: file name with extension to read, "test.dat" for example.

   :delimiter: delimiter between fields, tabulation by default.

   :skipinitialspace: if True, considers severals delimiters as only one : "\t\t" as '\t'.

   :skiprowsnb: number of rows to skip to get lines.

   :rowsnb: number of the rows to read, 1 by default.

   Returns:

   :colsnb: number of columns in all rows, 0 if rows have different number of columns

   :rows: rows.

   '''
   # Dispatch method ##############################################
   class From():
      @staticmethod
      def ascii():
         return iofiles.getlinesfrom_ascii(filename, delimiter, skipinitialspace, skiprowsnb, rowsnb)
      @staticmethod
      def netcdf():
         return iofiles.getlinesfrom_netcdf(filename)

   # Choose the input file format #################################
   if (fileformat == None):
      # ...TBD... Determine the format from file header
      pass

   if (fileformat == None):
      # Determine the format from filename extension
      file_extension = os.path.splitext(filenameslist[0])[1]
      fileformat = format_chooser.get(file_extension, None)
      ###
      #...TBD... raise an error if fileformat is unrecognized
      ###

   # Read the dataset from input file #############################
   if (fileformat in fileformat_getlist()):
      readfile = getattr(From, fileformat)
      return readfile()
   else:
      # Undefined file format #####################################
      # ...TBD... raise an error here !
      return None, None


def fileformat_getlist():
   '''
   Get list of format files availables

   Returns: list of file formats availables, ['ascii', ...]

   '''
   return iofiles.fileformat_getlist()


def pictureformat_getlist():
   '''
   Get list of pictures format availables

   Returns: list of picture formats availables, ['jpg', 'png', ...]

   '''
   return plot.getpictureformatlist()


def rasterformat_getlist():
   '''
   Get list of raster format files availables

   Returns : list of raster file formats availables, ['jpg', 'png', ...]

   '''
   return raster.getrasterformatlist()


def gridtype_getlist():
   ''' Return the list of the available GRD grid format ['surf7bin', 'surf6bin', ...].'''

   return iofiles.gridfiletype_getlist()


def gridformat_getlist():
   ''' Return the list of the available GRD grid format ['Surfer 7 binary grid', 'Surfer 6 binary grid', ...].'''

   return iofiles.gridfileformat_getlist()


def plottype_getlist():
   '''
   Get list of plot type availables

   Returns : list of plot type availables, ['2D_SURFACE', '2D_CONTOUR', ...]
   '''
   return plot.gettypelist()


def spectrum_plottype_getlist():
   '''Get list of available spectrum plot type.'''
   return spectral.getspectrum_plottype_list()


def rotation_angle_getlist():
   '''
   Get list of the available angles of rotation for the z_image.
   '''
   return genop.get_rotation_angle_list()


def festooncorrelation_getlist():
   '''
   To get the list of available festoon correlation methods.
   '''
   return genproc.getfestooncorrelationlist()


def destriping_getlist():
   '''
   To get the list of available destriping methods.

   '''
   return genproc.getdestripinglist()


def destripingreference_getlist():
   '''
   To get the list of available destriping reference calculation methods.

   '''
   return genproc.getdestripingreferencelist()


def destripingconfig_getlist():
   '''
   To get the list of available destriping configuration.

   '''
   return genproc.getdestripingconfiglist()


def regtrendmethod_getlist():
   '''
   To get the list of available destriping methods.

   '''
   return genproc.getregtrendmethodlist()


def regtrendcomp_getlist():
   '''
   To get the list of available destriping methods.

   '''
   return genproc.getregtrendcomplist()


def griddinginterpolation_getlist():
   '''
   To get the list of available gridding interpolation methods.

   '''
   return genop.getgriddinginterpolationlist()


def interpolation_getlist():
   '''
   Get list of interpolation methods availables

   Returns : list of interpolation methods availables, ['bilinear', 'bicubic', ...]

   '''
   return plot.getinterpolationlist()


def sensorconfig_getlist():
    ''' Returns the list of available magnetic sensor configurations. '''

    return magproc.getsensorconfiglist()


def structuralindex_getlist():
    ''' Returns the list of available structural index for Euler deconvolution. '''

    return magproc.getstructuralindexlist()

##def prosptech_getlist():
##   '''
##   Get list of prospection technicals availables
##
##   Returns : list of prospection technicals
##
##   '''
##   return magproc.getprosptechlist()


def colormap_getlist(sort=True):
   ''' Get the list of available colormaps.

   If sort is True, colormaps are sorted alphabetically ingoring the case.'''

   return colormap.getlist(sort=sort)


def colormap_icon_getpath():
   '''
   Getting the colormap icons path.

   Returns : path of availables colormap icon '**\plotting\colormapicons'

   '''
   return colormap.get_icon_path()


def colormap_icon_getlist():
   '''
   Getting the colormap icons list.

   Returns : list of availables colormap icon, ['gray_colormap_icon.jpg', ...]

   '''
   return colormap.get_icon_list()


def colormap_plot(cmname, creversed=False, fig=None, filename=None, dpi=None, transparent=False):
   '''
   Plots the colormap.

   Parameters :

   :cmname: Name of the colormap, 'gray_r' for example.

   :creversed: True to add '_r' at the cmname to reverse the color map

   :fig: figure to plot, None by default to create a new figure.

   :filename: Name of the color map file to save, None if no file to save.

   :dpi: 'dot per inch' definition of the picture file if filename != None

   :transparent: True to manage the transparency.

   Returns:

   :fig: Figure Object

   '''

   return colormap.plot(cmname, creversed, fig, filename, dpi, transparent)


def colormap_make_icon(cmname, path='', creversed=False, dpi=None):
   ''' Make an png icon of the given colormap name.

   Parameters
   ----------
   cmname : str
        Name of the colormap, 'gray_r' for example.

   path : str
        Path where to write the icon.

   creversed : bool
       True to add '_r' at the cmname to reverse the color map

   dpi : float
       'dot per inch' definition of the icon

   '''

   return colormap.make_icon(cmname, path=path, creversed=creversed, dpi=dpi)


def correlmap(dataset, method='Crosscor'):
    ''' Profile-to-profile correlation map.

    Profile-to-profile correlation map:
       * each odd profile in the dataset is incrementally shifted and the correlation coefficient computed against neighbouring profiles for each shift value
       * profiles are considered to be vertical, and the shift performed along the profile (hence vertically)
       * the correlation map size is then "twice the image vertical size" (shift may vary from -ymax to +ymax) by "number of profiles" (correlation is computed for each column listed in input)

    Parameters
    ----------

    method : str, {'Crosscor', 'Pearson', 'Spearman', 'Kendall'}
        Correlation method use.

    Returns
    -------

    cormap : 2-D array_like
        Profile-to-profile correlation map.

    pva1 : 2-D array_like
        Correlation weight map.

    '''

    return genproc.correlmap(dataset, method)


def correlshift(correlmap, pva1, corrmin=None, apod=None, output=None):
    ''' Maximum correlation shift.

    Compute the "best" shift to re-align/destagger dataset profiles.

    Parameters
    ----------
    correlmap : 2-D array_like
        Dataset correlation map.

    pva1 : 2-D array_like
        Dataset Correlation weight map.

    corrmin : float
        Minimum correlation value for profile shifting [0-1].

    apod : float
        Apodization threshold (in percent of the max correl coef)

    :output: correlation profile computed as a weighted mean across the correlation map ; the best shift value is found at this profile's maximum

    Returns:

    :shift: number of pixels to shift along the profile

    '''

    return genproc.correlshift(correlmap, pva1, corrmin=corrmin, apod=apod, output=output)

###
##
# ISIT Really useful here ?
##
###
def wallisoperator(cval, winval, setgain, targmean, targstdev, limitstdev, edgefactor):
    '''
    Computes the Wallis operator (brigthess contrast enhancement).  

    Parameters:

    :cval:  current window center value [f(x,y)]

    :winval: current window values

    :setgain: amplification factor for contrast [A]

    :targmean: target mean brightness level (typically between {0-255}) [m_d]

    :targstdev: target brightness standard deviation [\sigma_d]

    :limitstdev: maximal allowed window standard deviation (prevent infinitly high gain value if data are dispersed)

    :edgefactor: brightness forcing factor (controls ratio of edge to background intensities) [\alpha]

    Returns:
    
    :g_xy: Wallis operator at the current window center location [g(x,y)]
    
    '''
    return genproc.wallisoperator(cval, winval, setgain, targmean, targstdev, limitstdev, edgefactor)


help_path = os.path.join(os.path.dirname(__file__), 'help')
htmlhelp_filename = os.path.abspath(os.path.join(help_path, 'html', 'index.html'))
pdfhelp_filename = os.path.abspath(os.path.join(help_path, 'pdf', 'GeophPy.pdf'))

###
##
# Should be simply renamed get_help(), no ? 
##
###
def getgeophpyhelp(viewer='none', doctype='html'):
   '''
   To get help documentation of GeophPy module

   Parameters:

   :type: type of help needed, 'html' or 'pdf'.

   Returns:

   :helpcommand: application to start followed by pathname and filename of the 'html' or 'pdf' help document.

   '''

   

   path_selector = {
       'pdf' : pdfhelp_filename,
       'html' : htmlhelp_filename
       }

   pathfilename = path_selector[doctype]

##   if (doctype == 'pdf'):
##      pathfilename = pdfhelp_filename
##   else :
##      pathfilename = htmlhelp_filename

   if (viewer == 'none'):           # start automatically the best application 
       helpcommand = pathfilename
   else :
       helpcommand = viewer + " " + pathfilename
   return helpcommand

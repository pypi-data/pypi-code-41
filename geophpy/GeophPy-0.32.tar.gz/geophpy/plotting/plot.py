# -*- coding: utf-8 -*-
'''
    geophpy.plotting.plot
    ---------------------

    Module regrouping map plotting functions.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

import geophpy.plotting.plot2D as plot2D
import geophpy.plotting.plot3D as plot3D
import matplotlib.pyplot as plt
import numpy as np
from operator import itemgetter
import os

# list of plot types available
plottype_list = ['2D-SCATTER', '2D-SURFACE', '2D-CONTOUR', '2D-CONTOURF', '2D-POSTMAP']

# list of interpolations available
interpolation_list = ['none', 'nearest', 'bilinear', 'bicubic', 'spline16', 'sinc']    

# list of picture format files available
pictureformat_list = ['.eps', '.jpeg', '.jpg', '.pdf', '.pgf', '.png', '.ps', '.raw', '.rgba', '.svg', '.svgz', '.tif', '.tiff']

# list of matplotlib unfilled marker
unfilled_markers = plot2D.getunfilledmarkerlist()


def gettypelist():
   ''' Return the list of available plot types. '''

   return plottype_list


def getinterpolationlist():
   ''' Return the list of available interpolations for data display. '''

   return interpolation_list


def getpictureformatlist():
    ''' Return the list of available picture format. '''

    return pictureformat_list


def plot(dataset, plottype, cmapname, creversed=False, fig=None, filename=None, cmmin=None, cmmax=None, interpolation='bilinear', levels=None, cmapdisplay=True, axisdisplay=True, labeldisplay=False, pointsdisplay=False, dpi=None, transparent=False, logscale=False, rects=None, points=None, marker='+', markersize=None):
    ''' Dataset display.

    cf. `:meth:`~geophpy.dataset.DataSet.plot`

    '''

    ret = None

    if filename is None:
        success = True
    else:
        success = ispictureformat(filename)

    if success:
        # 2D-SURFACE
        if plottype.upper() in ['2D-SURFACE', 'SURFACE', 'SURF', 'SF']:
##                 interpolation='none', cmapdisplay=True, axisdisplay=True, labeldisplay=True, pointsdisplay=False,
##                 dpi=600, transparent=False, logscale=False, rects=None, points=None, marker='o'
            fig, cmap = plot2D.plot_surface(dataset, cmapname,
                                            creversed=creversed, fig=fig, filename=filename,
                                            cmmin=cmmin, cmmax=cmmax,
                                            interpolation=interpolation,
                                            cmapdisplay=cmapdisplay, axisdisplay=axisdisplay,
                                            labeldisplay=labeldisplay, pointsdisplay=pointsdisplay,
                                            dpi=dpi, transparent=transparent,
                                            logscale=logscale, rects=rects, points=points, marker=marker)

        # 2D-CONTOUR
        elif plottype.upper() in ['2D-CONTOUR', 'CONTOUR', 'CONT', 'CT']:
            fig, cmap = plot2D.plot_contour(dataset, cmapname, levels=levels, creversed=creversed, fig=fig, filename=filename, cmmin=cmmin, cmmax=cmmax, cmapdisplay=cmapdisplay, axisdisplay=axisdisplay, labeldisplay=labeldisplay, pointsdisplay=pointsdisplay, dpi=dpi, transparent=transparent, logscale=logscale, rects=rects, points=points, marker=marker)

        # 2D-CONTOUR (Filled)
        elif plottype.upper() in ['2D-CONTOURF', 'CONTOURF', 'CONTF', 'CF']:
            fig, cmap = plot2D.plot_contourf(dataset, cmapname, levels=levels, creversed=creversed, fig=fig, filename=filename, cmmin=cmmin, cmmax=cmmax, cmapdisplay=cmapdisplay, axisdisplay=axisdisplay, labeldisplay=labeldisplay, pointsdisplay=pointsdisplay, dpi=dpi, transparent=transparent, logscale=logscale, rects=rects, points=points, marker=marker)

        # 2D-SCATTER
        elif plottype in ['2D-SCATTER', 'SCATTER', 'SCAT', 'SC']:
            fig, cmap = plot2D.plot_scatter(dataset, cmapname, creversed=creversed, fig=fig, filename=filename, cmmin=cmmin, cmmax=cmmax, cmapdisplay=cmapdisplay, axisdisplay=axisdisplay, labeldisplay=labeldisplay, dpi=dpi, transparent=transparent, logscale=logscale, rects=rects, markersize=markersize)

        # 2D-POSTMAP
        elif plottype.upper() in ['2D-POSTMAP', 'POSTMAP', 'POST', 'PM']:
            fig, cmap = plot2D.plot_postmap(dataset, fig=fig, filename=filename, axisdisplay=axisdisplay, labeldisplay=labeldisplay, dpi=600, transparent=transparent, marker=marker, markersize=markersize)

        # '3D-SURFACE'
        else:
            fig, cmap = plot3D.plot_surface(dataset, cmapname, creversed, fig, filename, cmmin, cmmax, cmapdisplay, axisdisplay, dpi, transparent, logscale)

    else:
        fig = None
        cmap = None

    return fig, cmap


def completewithnan(dataset):
   """
   completes a data set with nan values in empty space
   """
   lbegin = 0
   nanpoints=[]
   
   x = dataset.data.values[0][0]
   for l in range(len(dataset.data.values)):
      if (dataset.data.values[l][0] != x):
         # treats the previous profile
         lend = l
         delta_y = _profile_mindelta_get(dataset.data.values[lbegin:lend])
         _profile_completewithnan(dataset.data.values[lbegin:lend],delta_y,dataset.info.y_min, dataset.info.y_max, nanpoints)
         lbegin = l
         # if the previous profile is not next, adds nan profiles to avoid linearisations on the plot
         if ((dataset.data.values[l][0] - x) > dataset.info.x_mindelta):
            # nan profile created just after the previous profile
            _profile_createwithnan(nanpoints, x+(dataset.info.x_mindelta/10),dataset.info.y_min, dataset.info.y_max)
            # nan profile created just before the current profile
            _profile_createwithnan(nanpoints, dataset.data.values[l][0]-(dataset.info.x_mindelta/10),dataset.info.y_min, dataset.info.y_max)
         x = dataset.data.values[l][0]
         
   # treats the last profile
   delta_y = _profile_mindelta_get(dataset.data.values[lbegin:])
   _profile_completewithnan(dataset.data.values[lbegin:],delta_y,dataset.info.y_min, dataset.info.y_max, nanpoints)

   # adds the nan points to the values array
                                                            # converts in a numpy array, sorted by column 0 then by column 1.
   try:
      dataset.data.values = np.array(sorted(np.concatenate((dataset.data.values, nanpoints)), key=itemgetter(0,1)))
   except:
      None


def ispictureformat(picturefilename):
   '''
   Detects if the picture format is available
   '''
   splitedfilename = os.path.splitext(picturefilename)
   extension = (splitedfilename[-1]).lower()

   ispictureformat = False
   for ext in pictureformat_list:
      if (extension == ext):
         ispictureformat = True
         break

   return ispictureformat



def _profile_completewithnan(profile,delta_y,dataset_ymin, dataset_ymax, nanpoints):
   """
   completes a profile with nan value in empty space
   """
   coef = 20                        

   if (dataset_ymin != None):             # if ymin is not equal to None
      profile[0][1] = dataset_ymin        # normalizes all begins of profiles with the same value
      
   yprev = profile[0][1]                  # initialises previous y
   valprev = profile[0][2]                # initialises previous value

   for p in profile:                      # for each point in the profile
      y = p[1]                            # y is the column 1 value
      if (((y-yprev) > coef*delta_y) or np.isnan(p[2]) or np.isnan(valprev)):
         yn = yprev + ((y-yprev)/1000)
         while (yn < y):
            nanpoints.append([p[0], yn, np.nan])
            yn = yn + ((y-yprev)/10)
         nanpoints.append([p[0], y - ((y-yprev)/1000), np.nan])
      yprev = y                           # saves the y value as the previous for profile to be
      valprev = p[2]                      # saves the value as the previous for profile to be

   # treats the last point of profile
   if ((dataset_ymax-yprev) > coef*delta_y):
      y = yprev + ((dataset_ymax-yprev)/1000)
      while (y < dataset_ymax):
         nanpoints.append([p[0], y, np.nan])
         y = y + ((dataset_ymax-yprev)/10)
      


def _profile_createwithnan(nanpoints, x,dataset_ymin, dataset_ymax):
   """
   creates a profile with nan values
   """

   if ((dataset_ymin != None) and (dataset_ymax != None)):
      for y in range(int(dataset_ymin), int(dataset_ymax)):
         nanpoints.append([x, y, np.nan])



def _profile_mindelta_get(profile):
   '''
   Get Minimal Delta between 2 values in a same profile.
   '''
   l = 0
   deltamin = 0
   while (deltamin == 0):
      deltamin = abs(profile[l+1][1] - profile[l][1])
      l = l+1
      
   yprev = profile[l][1]

   for p in profile[l+1:]:
      delta = abs(p[1] - yprev)
      if ((delta != 0) and (delta < deltamin)):         
         deltamin = delta

   return deltamin

def coord2rec(xmin, xmax, ymin, ymax):
    '''
    Convert rectangle extent coordinates to bottom left corner,
    width and height coordinates.

    '''

    x = min(xmin,xmax)
    y = min(ymin,ymax)
    w = abs(xmax-xmin)
    h = abs(ymax-ymin)

    return [x, y, w, h]


def extents2rectangles(extentlist):
    '''
    Convert a list of rectangle extent coordinates to a list of
    bottom left corner width and height coordinates.

    '''

    rectanglelist = []

    for extent in extentlist:
       rectanglelist.append(coord2rec(*extent))

    return rectanglelist
   
def _init_figure(fig=None):
    ''' Clear the given figure or return a new one and initialize an ax. '''

    # First display
    if fig is None:
        fig = plt.figure()
        #fig = Figure()
        #FigureCanvas(fig)

    # Existing display
    else:
        fig = plt.figure(fig.number, clear=True)
        #fig.clf()

    # Axes initialization
    ax = fig.add_subplot(111)

    return fig, ax

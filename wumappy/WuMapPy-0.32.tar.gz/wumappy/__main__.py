# -*- coding: utf-8 -*-
'''
    wumappy
    -------

    The public API and command-line interface to WuMapPy package.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

import os
import sys
import argparse
#------------------------------------------------------------------------------#
# Trying to handle both PySide, Qt4 and PySide2, Qt5                           #
#------------------------------------------------------------------------------#
#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *
##try:
##    from PySide import QtCore, QtGui
##    from PySide.QtGui import *
##    from PySide.QtCore import *
##    is_qt4 = True
##    is_qt5 = not is_qt4
##
##except ImportError:
##    from PySide2 import QtCore, QtGui, QtWidgets
##    from PySide2.QtGui import *
##    from PySide2.QtCore import *
##    from PySide2.QtWidgets import *
##    is_qt5 = True
##    is_qt4 = not is_qt5

### TODO Detect PyQt or Pyside to set QT_API properly
##
# Forcing matplotlib within a Qt application to use PySide binding
## (default is PyQt4). The QT_API environment variable is set to 'PySide'
##import matplotlib
##matplotlib.use('Qt4Agg')
##matplotlib.rcParams['backend.qt4']='PySide' #(rcParams has been depreciated in recent matplotlib versions).

# Setting up the QT_API environment variable so matplotlib within a Qt application uses the proper binding.
if __binding__ in ('PyQt5', 'PySide2'):
    os.environ['QT_API'] = 'pyqt5'
elif __binding__ == 'PyQt4':
    os.environ['QT_API'] = 'pyqt4'
elif __binding__ == 'PySide':
    os.environ['QT_API'] = 'pyside'

###
##
# Debbug printing for Qt Bindings
if False:
    print('***')
    print('Using "', __binding__, '" binding')
##
###

##if is_qt4:
##    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
##else:
##    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
##
##from matplotlib.figure import Figure

#------------------------------------------------------------------------------#
# WuMapPy's import                                                             #
#------------------------------------------------------------------------------#
from wumappy import SOFTWARE, VERSION, AUTHORS, DATE, DESCRIPTION
from wumappy.gui.common.menubar import MenuBar
from wumappy.gui.dataset.datasetwindow import DatasetWindow
from wumappy.gui.geoposset.geopossetwindow import GeopossetWindow
from wumappy.gui.opendatasetdlgbox import OpenDatasetDlgBox
from wumappy.gui.opengeopossetdlgbox import OpenGeopossetDlgBox
from wumappy.gui.guisettingsdlgbox import GuiSettingsDlgBox
from wumappy.gui.languagedlgbox import LanguageDlgBox
from wumappy.misc.asciiset import AsciiSet
from wumappy.misc.configset import ConfigSet
#from wumappy.gui.common.menubar import *
#from wumappy.gui.common.warningdlgbox import *
#from wumappy.gui.dataset.datasetwindow import *
#from wumappy.gui.geoposset.geopossetwindow import *
#from wumappy.gui.opendatasetdlgbox import *
#from wumappy.gui.opengeopossetdlgbox import *
#from wumappy.gui.guisettingsdlgbox import *
#from wumappy.gui.languagedlgbox import *
#from wumappy.misc.asciiset import *
#from wumappy.misc.configset import *

#-----------------------------------------------------------------------------#
# GeophPy's import                                                            #
#-----------------------------------------------------------------------------#
import geophpy
#from geophpy.dataset import *
from geophpy.dataset import DataSet, getgeophpyhelp#, format_chooser as gpy_format_chooser
import geophpy.filesmanaging.files as iofiles
#from geophpy.geoposset import *

#-----------------------------------------------------------------------------#
# Frozen/Unfrozen state                                                       #
#-----------------------------------------------------------------------------#
import imp  # used for package search when frozen state
# Path determination for logo & images
if getattr(sys, 'frozen', False):
    # Frozen application
##    __file__ = os.path.dirname(sys.executable)
    lib_dir = os.path.realpath(imp.find_module("wumappy")[1])
else:
    # Not frozen application
##    __file__ = os.path.dirname(os.path.realpath(__file__))
    lib_dir = os.path.dirname(os.path.realpath(__file__))

#-----------------------------------------------------------------------------#
# Warning display                                                             #
#-----------------------------------------------------------------------------#
### Forcing warning display for debugging
import warnings
warnings.simplefilter("always")

# Do not display console warning for zero division
import numpy as np
np.seterr(divide='ignore', invalid='ignore')


#-----------------------------------------------------------------------------#
# WuMapPy GUI                                                                 #
#-----------------------------------------------------------------------------#
# ITEM Id code definition
ITEM_SEPARATOR = 0
ITEM_FILES = 1
ITEM_SETTINGS = 2
ITEM_HELP = 3
ITEM_DATASET = 10
ITEM_DATASET_OPEN = 11
ITEM_DATASET_IMPORT = 12
ITEM_DATASET_OPENASCIIFILES = 13
ITEM_DATASET_OPENGRIDFILES = 14
ITEM_GEOPOSSET = 15
ITEM_GEOPOSSET_OPEN = 16
ITEM_GEOPOSSET_IMPORT = 17
ITEM_GEOPOSSET_OPENSHAPEFILES = 18
ITEM_EXIT = 19
ITEM_LANGUAGE = 20
ITEM_FONT = 21
ITEM_MISCSETTINGS = 22
ITEM_ABOUT = 30
ITEM_WUMAPPYHELP = 31
ITEM_WUMAPPYPDFUSERMANUAL = 311
ITEM_WUMAPPYHTMLUSERMANUAL = 312
ITEM_GEOPHPYHELP = 32
ITEM_GEOPHPYPDFUSERMANUAL = 321
ITEM_GEOPHPYHTMLUSERMANUAL = 322

class WuMapPyGui(QWidget):

    def __init__(self):
        # definitions
        self.currentdatasetwindowsindex = 1
        self.currentgeopossetwindowsindex = 1
        self.datasetwindowslist = []        # list of data set windows
        self.geopossetwindowslist = []      # list of geographic position set windows

        super(WuMapPyGui, self).__init__()

        self.wid = self
        self.configset = ConfigSet()
        self.asciiset = AsciiSet(self.configset.get('ASCII', 'Optima Bold'), self.configset.getint('ASCII', '10'))              # creates an ascii string set #AB# Modification Font + Size
        self.asciiset.setLanguage(self.configset.get('ASCII', 'language'))
        self.wid.setFont(self.asciiset.font)    # sets the font before creating menu bar


        # ITEM_Id, ITEM_NameId, ITEM_Action, ITEM_Comment, Parent_Id, IsEnabled Function
        self.ItemList = [
                        ## Files menu ##############################################################
                        [ITEM_FILES, 'FILES_ID', "Menu", "", None, True],
                        [ITEM_DATASET, 'DATASET_ID', None, "", ITEM_FILES, True],
                        # Data set -----------------------------------------------------------------
                        [ITEM_DATASET_OPEN, 'OPEN_ID', self.opendataset, "Builds data set from netcdf files", ITEM_FILES, True],
                        [ITEM_DATASET_IMPORT, 'IMPORT_ID', "Menu", "", ITEM_FILES, True],
                        [ITEM_DATASET_OPENASCIIFILES, 'FROMASCIIFILES_ID', self.opendatasetfromasciifiles, "Builds data set from ASCII files", ITEM_DATASET_IMPORT, True],
                        [ITEM_DATASET_OPENASCIIFILES, 'FROMGRIDIFILES_ID', self.opendatasetfromgridfiles, "Builds data set from  Surfer grid (.grd) files", ITEM_DATASET_IMPORT, True],
                        # Geographic position set --------------------------------------------------
                        [ITEM_SEPARATOR, '', "Separator", "", ITEM_FILES, True],
                        [ITEM_GEOPOSSET, 'GEOPOSSET_ID', None, "", ITEM_FILES, True],
                        [ITEM_GEOPOSSET_OPEN, 'OPEN_ID', self.opengeoposset, "Builds geographics positions set from netcdf files", ITEM_FILES, True],
                        [ITEM_GEOPOSSET_IMPORT, 'IMPORT_ID', "Menu", "", ITEM_FILES, True],
                        [ITEM_GEOPOSSET_OPENSHAPEFILES, 'FROMSHAPEFILES_ID', self.opengeopossetfromshapefile, "Builds geographics positions set from shape files", ITEM_GEOPOSSET_IMPORT, True],
                        # Exit ---------------------------------------------------------------------
                        [ITEM_SEPARATOR, '', "Separator", "", ITEM_FILES, True],
                        [ITEM_EXIT, 'EXIT_ID', self.exit, "Exits WuMapPy Application", ITEM_FILES, True],
                        ## Settings menu ###########################################################
                        [ITEM_SETTINGS, 'SETTINGS_ID', "Menu", "", None, True],
                        [ITEM_LANGUAGE, 'LANGUAGE_ID', self.language, "", ITEM_SETTINGS, True],
                        [ITEM_FONT, 'FONT_ID', self.font, "", ITEM_SETTINGS, True],
                        [ITEM_MISCSETTINGS, 'MISCSETTINGS_ID', self.settings, "", ITEM_SETTINGS, True],
                        ## Help menu ###############################################################
                        [ITEM_HELP, 'HELP_ID', "Menu", "", None, True],
                        [ITEM_ABOUT, 'ABOUT_ID', self.about, "", ITEM_HELP, True],
                        [ITEM_WUMAPPYHELP, 'WUMAPPYHELP_ID', "Menu", "", ITEM_HELP, True],
                        [ITEM_WUMAPPYHTMLUSERMANUAL, 'HTMLUSERMANUAL_ID', self.wumappyhtmlhelp, "", ITEM_WUMAPPYHELP, True],
                        [ITEM_WUMAPPYPDFUSERMANUAL, 'PDFUSERMANUAL_ID', self.wumappypdfhelp, "", ITEM_WUMAPPYHELP, True],
                        [ITEM_GEOPHPYHELP, 'GEOPHPYHELP_ID', "Menu", "", ITEM_HELP, True],
                        [ITEM_GEOPHPYHTMLUSERMANUAL, 'HTMLUSERMANUAL_ID', self.geophpyhtmlhelp, "", ITEM_GEOPHPYHELP, True],
                        [ITEM_GEOPHPYPDFUSERMANUAL, 'PDFUSERMANUAL_ID', self.geophpypdfhelp, "", ITEM_GEOPHPYHELP, True]]

        self.LanguageItemList = []        # list of languages action items (item_num, item_id)

        self.menubar = MenuBar.from_list(self.ItemList, self)

        # Icons from the resources folder ############################
##        self.resources_path = os.path.join(__file__, 'resources')
        self.resources_path = os.path.join(lib_dir, 'resources')
        logo_path = os.path.abspath(os.path.join(self.resources_path, 'wumappy.png'))
        self.icon = QIcon(logo_path)
        self.wid.setWindowIcon(self.icon)
        self.wid.setWindowTitle(SOFTWARE)
        self.fillingwindow()


    def fillingwindow(self):
        ''' Populate the window. '''

        logo_path = os.path.abspath(os.path.join(self.resources_path, 'wumappy.png'))
        layout = QVBoxLayout()                # builds the main layout
        self.layout = layout
        layout1 = QGridLayout()
        layout1.setRowMinimumHeight(0, self.menubar.height)
        layout2 = QHBoxLayout()
        layout3 = QVBoxLayout()

        layout.addLayout(layout1)                                           # First layout to avoid overwriting with menubar
        layout.addLayout(layout2)
        qlogo = QLabel()                                              # Adds the WuMapPy logo
        qlogo.setPixmap(QPixmap(logo_path))
        layout2.addWidget(qlogo)
        layout2.addLayout(layout3)

        # Software title
        title_font = QFont()
        title_font.setFamily("Lucida Handwriting")
        title_font.setPointSize(35)
        title_label = QLabel('%s' % SOFTWARE, self.wid)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout3.addWidget(title_label)

        # Software version
        version_font = QFont()
        version_font.setFamily("times")
        version_font.setPointSize(13)
        version_label = QLabel('v%s - %s' % (VERSION, DATE), self.wid)     # defines the software version and date
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout3.addWidget(version_label)

        # Software Description
        descript_label = QLabel('%s' % DESCRIPTION, self.wid)               # defines the software description
        descript_label.setFont(version_font)
        descript_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout3.addWidget(descript_label)

        layout.setSizeConstraint(QLayout.SetFixedSize)                # to not authorize size modification
        self.wid.setLayout(layout)


        ### TO DO, issue with font size -> always need to through font settings to make it ok....
##        print('****',self.configset.get('ASCII', 'fontname'))
##        print('****',self.configset.get('ASCII', 'fontsize'))
##        self.menubar.update()
        ###
        self.wid.show()



    def closeEvent(self, event):
        '''
        Configures the close event of the main window
        '''
        self.exit()


    def opendataset(self):
        '''
        Builds data set from one or several files
        '''
        success = False
        directory = self.configset.get('DIRECTORIES', 'openfiledir')

        #filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', dir=directory, filter='*.nc')
        ## PyQt5's getOpenFileNames has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getOpenFileNames(parent, title, directory, initialFilter, options)
        filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', directory, '*.nc')

##        qfiledlg = QFileDialog(self.wid, directory = directory, filter='*.nc', options=QFileDialog.DontUseNativeDialog)
##        qfiledlg.setFont(self.asciiset.font)
##        qfiledlg.setGeometry(self.geometry().left(), self.geometry().top(), qfiledlg.geometry().width(), qfiledlg.geometry().height())
##        qfiledlg.show()
##        qfiledlg.exec()
##        if (qfiledlg.result() == QDialog.Accepted):
            #filenames = qfiledlg.selectedFiles()
        # File selected (empty (False) if cancel is clicked)
        if filenames:
            # Conversion to list for single file name
            if isinstance(filenames, str):
                filenames = [filenames]

            # Opening file
            success, dataset = DataSet.from_file(filenames, fileformat='netcdf')

            # Opening Dataset windows
            if success:
                colormap = self.configset.get('DISPSETTINGS', 'colormap')
                reverseflag = self.configset.getboolean('DISPSETTINGS', 'reverseflag')
                plottype = self.configset.get('DISPSETTINGS', 'plottype')
                interpolation = self.configset.get('DISPSETTINGS', 'interpolation')
                colorbardisplayflag = self.configset.getboolean('DISPSETTINGS', 'colorbardisplayflag')
                axisdisplayflag = self.configset.getboolean('DISPSETTINGS', 'axisdisplayflag')
                dpi = self.configset.getint('DISPSETTINGS', 'dpi')
                colorbarlogscaleflag = self.configset.getboolean('DISPSETTINGS', 'colorbarlogscaleflag')
                self.configset.set('DIRECTORIES', 'openfiledir', os.path.dirname(filenames[0]))

                title = "DataSet" + str(self.currentdatasetwindowsindex)
                self.currentdatasetwindowsindex += 1
                window = DatasetWindow.new(self,
                                           title,
                                           dataset,
                                           self.geopossetwindowslist,
                                           plottype,
                                           colormap,
                                           interpolation,
                                           reverseflag=reverseflag,
                                           colorbarlogscaleflag=colorbarlogscaleflag,
                                           dpi=dpi,
                                           colorbardisplayflag=colorbardisplayflag,
                                           axisdisplayflag=axisdisplayflag)
                self.datasetwindowslist.append(window)
                window.view()

        return success


    ###
    ##
    # Regroup with opendataset
    ##
    ###
    def opendatasetfromgridfiles(self):
        ''' Build dataset from one or several Surfer grid files. '''

        success = False

        directory = self.configset.get('DIRECTORIES', 'importfiledir')

        # Multiple files
        #filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', dir=directory, filter=('GRD Surfer Grid (*.grd)'))
        ## PyQt5's getOpenFileNames has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getOpenFileNames(parent, title, directory, initialFilter, options)
##        ###
##        filters = ('GRD Surfer Grid (*.grd)'
##                   ';;'
##                   'ASCII files (*.csv *.dat *.txt *.xyz)'
##                   ';;'
##                   'All (*.*)')
##        filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', directory, filters)
        ###
        filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', directory, 'GRD Surfer Grid (*.grd)')

        # File selected (empty (False) if cancel is clicked)
        if filenames:
            # Conversion to list for single file name
            if isinstance(filenames, str):
                filenames = [filenames]
            success, dataset = DataSet.from_file(filenames, fileformat='surfer')
            #success, dataset = DataSet.from_file(filenames)

            # Opening Dataset windows
            if success:
                # Default display properties
                colormap = self.configset.get('DISPSETTINGS', 'colormap')
                reverseflag = self.configset.getboolean('DISPSETTINGS', 'reverseflag')
                plottype = self.configset.get('DISPSETTINGS', 'plottype')
                interpolation = self.configset.get('DISPSETTINGS', 'interpolation')
                colorbardisplayflag = self.configset.getboolean('DISPSETTINGS', 'colorbardisplayflag')
                axisdisplayflag = self.configset.getboolean('DISPSETTINGS', 'axisdisplayflag')
                dpi = self.configset.getint('DISPSETTINGS', 'dpi')
                colorbarlogscaleflag = self.configset.getboolean('DISPSETTINGS', 'colorbarlogscaleflag')

                # Dataset windows creation
                #title = "DataSet" + str(self.currentdatasetwindowsindex)
                title = "DataSet" + str(self.currentdatasetwindowsindex)
                window = DatasetWindow.new(self,
                                           title,
                                           dataset,
                                           self.geopossetwindowslist,
                                           plottype,
                                           colormap,
                                           interpolation,
                                           reverseflag=reverseflag,
                                           colorbarlogscaleflag=colorbarlogscaleflag,
                                           dpi=dpi,
                                           colorbardisplayflag=colorbardisplayflag,
                                           axisdisplayflag=axisdisplayflag)
                self.datasetwindowslist.append(window)
                window.view()

                # updating configuration file
                self.configset.set('DIRECTORIES', 'importfiledir', os.path.dirname(os.path.realpath(filenames[0])))

    ###
    ##
    # Regroup with opendataset
    ##
    ###
    def opendatasetfromasciifiles(self):
        '''
        Builds data set from one or several text files
        '''
        success = False

        directory = self.configset.get('DIRECTORIES', 'importfiledir')

        # Multiple files
        #filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', dir=directory)
        ## PyQt5's getOpenFileNames has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getOpenFileNames(parent, title, directory, initialFilter, options)
        filenames, selectedfilter = QFileDialog.getOpenFileNames(self, 'Open file', directory)

        # File selected (empty (False) if cancel is clicked)
        if filenames:
            # Conversion to list
            if isinstance(filenames, str):
                filenames = [filenames]

            # Automatic search for file delimiter
            delimiter = iofiles.sniff_delimiter(filenames[0])

            # Or using default value
            #if not success:
            if delimiter is None:
                delimiter = self.configset.get('FILES', 'delimiter')
            if delimiter == 'space':
                delimiter = ' '
            elif delimiter == 'tab':
                delimiter = '\t'

            self.configset.set('DIRECTORIES', 'importfiledir', os.path.dirname(os.path.realpath(filenames[0])))

            # Default parameters from configuration file #######################
            # File format
            fileformat = self.configset.get('FILES', 'fileformat')
            delimitersasuniqueflag = self.configset.getboolean('FILES', 'delimitersasuniqueflag')

            skiprows = self.configset.getint('FILES', 'skiprows')
            fieldsrow = self.configset.getint('FILES', 'fieldsrow')
            xcolnum = self.configset.getint('GENSETTINGS', 'xcolnum')
            ycolnum = self.configset.getint('GENSETTINGS', 'ycolnum')
            zcolnum = self.configset.getint('GENSETTINGS', 'zcolnum')

            # Gridding
            stepxgridding = self.configset.getfloat('GENSETTINGS', 'stepxgridding')
            stepygridding = self.configset.getfloat('GENSETTINGS', 'stepygridding')
            interpgridding = self.configset.get('GENSETTINGS', 'interpgridding')
            autogriddingflag = self.configset.getboolean('GENSETTINGS', 'autogriddingflag')
            dispdatapointflag = self.configset.getboolean('GENSETTINGS', 'dispdatapointflag')

            # Filters
            zeromeanfiltflag = self.configset.getboolean('PROCESSING', 'zeromeanfiltflag')
            zeromeanfiltvar = self.configset.get('PROCESSING', 'zeromeanfiltvar')

            festoonfiltflag = self.configset.getboolean('PROCESSING', 'festoonfiltflag')
            festoonfiltmethod = self.configset.get('PROCESSING', 'festoonfiltmethod')
            festoonfiltshift = self.configset.getint('PROCESSING', 'festoonfiltshift')
            festoonfiltcorrmin = self.configset.getfloat('PROCESSING', 'festoonfiltcorrmin')

            # Display
            colormap = self.configset.get('DISPSETTINGS', 'colormap')
            reverseflag = self.configset.getboolean('DISPSETTINGS', 'reverseflag')
            colorbarlogscaleflag = self.configset.getboolean('DISPSETTINGS', 'colorbarlogscaleflag')
            coloredhistoflag = self.configset.getboolean('DISPSETTINGS', 'coloredhistoflag')

            # Import Dataset Dialogbox creation ################################
            r, openfiles = OpenDatasetDlgBox.new("Open Data Set",
                                                 filenames,
                                                 parent=self,
                                                 xcolnum=xcolnum,
                                                 ycolnum=ycolnum,
                                                 zcolnum=zcolnum,
                                                 delimiter=delimiter,
                                                 fileformat=fileformat,
                                                 delimitersasuniqueflag=delimitersasuniqueflag,
                                                 skiprows=skiprows,
                                                 fieldsrow=fieldsrow,
                                                 interpgridding=interpgridding,
                                                 stepxgridding=stepxgridding,
                                                 stepygridding=stepygridding,
                                                 autogriddingflag=autogriddingflag,
                                                 dispdatapointflag=dispdatapointflag,
                                                 zeromeanfiltflag=zeromeanfiltflag,
                                                 zeromeanfiltvar=zeromeanfiltvar,
                                                 festoonfiltflag=festoonfiltflag,
                                                 festoonfiltmethod=festoonfiltmethod,
                                                 festoonfiltshift=festoonfiltshift,
                                                 festoonfiltcorrmin=festoonfiltcorrmin,
                                                 colormap=colormap,
                                                 reverseflag=reverseflag,
                                                 coloredhistoflag=coloredhistoflag)


            if r == QDialog.Accepted:
                success = True
                dataset = openfiles.dataset
                zmin = openfiles.zmin
                zmax = openfiles.zmax
                colormap = openfiles.colormap
                colorbarlogscaleflag = openfiles.colorbarlogscaleflag
                reverseflag = openfiles.reverseflag
            else:
                success = False

            if success:
                ### Displaced in # update conf file for coherency
##                self.configset.set('DISPSETTINGS', 'colormap', str(colormap))
##                self.configset.set('DISPSETTINGS', 'reverseflag', str(reverseflag))
##                self.configset.set('DISPSETTINGS', 'colorbarlogscaleflag', str(colorbarlogscaleflag))
                ###

                # Dataset Window creation ######################################
                plottype = self.configset.get('DISPSETTINGS', 'plottype')
                interpolation = self.configset.get('DISPSETTINGS', 'interpolation')
                colorbardisplayflag = self.configset.getboolean('DISPSETTINGS', 'colorbardisplayflag')
                axisdisplayflag = self.configset.getboolean('DISPSETTINGS', 'axisdisplayflag')
                dpi = self.configset.getint('DISPSETTINGS', 'dpi')

                title = "DataSet" + str(self.currentdatasetwindowsindex)
                self.currentdatasetwindowsindex += 1
                window = DatasetWindow.new(self, title, dataset, self.geopossetwindowslist,
                                           plottype, colormap, interpolation, reverseflag=reverseflag,
                                           colorbarlogscaleflag=colorbarlogscaleflag, zmin=zmin, zmax=zmax,
                                           dpi=dpi, colorbardisplayflag=colorbardisplayflag,
                                           axisdisplayflag=axisdisplayflag)
                self.datasetwindowslist.append(window)
                window.view()

                # updating configuration file ##################################
                # File format
                self.configset.set('FILES', 'fileformat', openfiles.fileformat)
                if openfiles.delimiter == ' ':
                    delimiter = 'space'
                elif openfiles.delimiter == '\t':
                    delimiter = 'tab'
                else:
                    delimiter = openfiles.delimiter

                self.configset.set('FILES', 'delimiter', delimiter)
                self.configset.set('FILES', 'delimitersasuniqueflag', str(openfiles.delimitersasuniqueflag))

                self.configset.set('FILES', 'skiprows', str(openfiles.skiprows))
                self.configset.set('FILES', 'fieldsrow', str(openfiles.fieldsrow))

                self.configset.set('GENSETTINGS', 'xcolnum', str(openfiles.x_colnum))
                self.configset.set('GENSETTINGS', 'ycolnum', str(openfiles.y_colnum))
                self.configset.set('GENSETTINGS', 'zcolnum', str(openfiles.z_colnum))

                # Gridding
                self.configset.set('GENSETTINGS', 'autogriddingflag', str(openfiles.autogriddingflag))
                self.configset.set('GENSETTINGS', 'dispdatapointflag', str(openfiles.dispdatapointflag))
                self.configset.set('GENSETTINGS', 'stepxgridding', str(openfiles.stepxgridding))
                self.configset.set('GENSETTINGS', 'stepygridding', str(openfiles.stepygridding))
                self.configset.set('GENSETTINGS', 'interpgridding', str(openfiles.interpgridding))

                # Filters
                self.configset.set('PROCESSING', 'zeromeanfiltflag', str(openfiles.zeromeanfiltflag))
                self.configset.set('PROCESSING', 'zeromeanfiltvar', str(openfiles.zeromeanfiltvar))

                self.configset.set('PROCESSING', 'festoonfiltmethod', str(openfiles.festoonfiltmethod))
                self.configset.set('PROCESSING', 'festoonfiltshift', str(openfiles.festoonfiltshift))
                self.configset.set('PROCESSING', 'festoonfiltcorrmin', str(openfiles.festoonfiltcorrmin))
                self.configset.set('PROCESSING', 'festoonfiltflag', str(openfiles.festoonfiltflag))

                # Display
                self.configset.set('DISPSETTINGS', 'colormap', str(colormap))
                self.configset.set('DISPSETTINGS', 'reverseflag', str(reverseflag))
                self.configset.set('DISPSETTINGS', 'colorbarlogscaleflag', str(colorbarlogscaleflag))

##                else:  # was with the if(len(filenames)>0: to be deleted if works
##                    QErrorMessage()

        return success

    def opengeoposset(self):
        '''
        Builds geographic positions set from one or several ascii files
        '''
        success = self._opengeoposset(filters='*.csv *.txt *.dat', filetype='ascii')
        return success

    def opengeopossetfromshapefile(self):
        '''
        Builds positions set from one or several shape files
        '''
        success = self._opengeoposset(filters='*.shp', filetype='shapefile')
        return success

    def _opengeoposset(self, filters='*', filetype='ascii'):
        '''
        Builds positions set from one or several files
        '''
        success = True

        directory = self.configset.get('DIRECTORIES', 'opengeopossetfiledir')

        # Single file
        #filenames, selectedfilter = QFileDialog.getOpenFileName(self,'Open file',dir=directory, filter=filters)
        ## PyQt5's getOpenFileName has no 'dir' but a 'directory' key.
        ## no keys are used to prevent errors when using a different Qt binding for Python
        ## General call :
        ## getOpenFileName(parent, title, directory, initialFilter, options)
        filenames, selectedfilter = QFileDialog.getOpenFileName(self, 'Open file', directory, filters)

        # File selected (empty (False) if cancel is clicked)
        initcursor = self.wid.cursor() # Wait cursor
        self.wid.setCursor(Qt.WaitCursor)
        if filenames:
            # Conversion to list
            if isinstance(filenames, str):
                filenames = [filenames]

            self.configset.set('DIRECTORIES', 'opengeopossetfiledir', os.path.dirname(os.path.realpath(filenames[0])))

            refsystem = self.configset.get('GEOPOSITIONING', 'refsystem')
            utm_letter = self.configset.get('GEOPOSITIONING', 'utm_letter')
            utm_number = self.configset.getint('GEOPOSITIONING', 'utm_number')

            try :
                r, openfiles = OpenGeopossetDlgBox.new("Open Geographic Positions Set From " + filetype, filetype, filenames, refsystem, utm_number, utm_letter, self)
                if r == QDialog.Accepted:
                    geoposset = openfiles.geoposset
                    title = "GeoPosSet" + str(self.currentgeopossetwindowsindex)
                    self.currentgeopossetwindowsindex += 1
                    window = GeopossetWindow.new(self, title, geoposset, None)
                    self.geopossetwindowslist.append(window)
                    window.view()
                    self.configset.set('GEOPOSITIONING', 'refsystem', str(openfiles.geoposset.refsystem))
                    self.configset.set('GEOPOSITIONING', 'utm_letter', str(openfiles.geoposset.utm_letter))
                    self.configset.set('GEOPOSITIONING', 'utm_number', str(openfiles.geoposset.utm_number))

                    # updates all data set windows
                    for datasetwindow in self.datasetwindowslist:
                        datasetwindow.menubar.update()

            except:
                QErrorMessage()

        # Init cursor
        self.wid.setCursor(initcursor)

        return success



    def settings(self):
        ''' Edits main GUI Settings. '''

        r, guisettings = GuiSettingsDlgBox.new("User Interface Settings", self)
        if r == QDialog.Accepted:
            self.configset.set('MISC', 'realtimeupdateflag', str(guisettings.realtimeupdateflag))
            self.configset.set('MISC', 'changeresolutionflag', str(guisettings.changeresolutionflag))

    def language(self):
        ''' Edit language Settings. '''

        r, language = LanguageDlgBox.new("Language Settings", self)
        if r == QDialog.Accepted:
                                                                # gets new ascii set language and font
            self.asciiset = language.asciiset
                                                                # updates configuration file
            self.configset.set('ASCII', 'language', self.asciiset.lnglist[self.asciiset.lngindex].name)

                                                                # updates menu bar with new language or font
            self.menubar.update()
                                                                # updates all data set windows
            for datasetwindow in self.datasetwindowslist:
                datasetwindow.menubar.update()
                                                                # updates all geopos set windows
            for geopossetwindow in self.geopossetwindowslist:
                geopossetwindow.menubar.update()

    def about(self):
        '''
        Displays informations about application
        '''
        text = SOFTWARE + " V" + VERSION  + "\tDate: " + DATE + "\n" + DESCRIPTION + "\n\n" + geophpy.__software__ + " V" + geophpy.__version__ + "\tDate: " + geophpy.__date__ + "\n" + geophpy.__description__ + "\n\nAuthors: " + AUTHORS
        about = QMessageBox(self.wid)
        about.setGeometry(self.geometry().left(), self.geometry().top(), about.geometry().width(), about.geometry().height())
        about.setFont(self.asciiset.font)
        about.setWindowTitle(self.asciiset.getStringValue('ABOUT_ID'))
        about.setText(text)
        about.show()
        about.exec()

    def wumappypdfhelp(self):
        ''' Start pdf user guide for wumappy . '''

        viewer = self.configset.get("MISC", "pdf_viewer")
        os.system(getwumappyhelp(viewer, 'pdf'))

    def wumappyhtmlhelp(self):
        ''' Start html user guide for wumappy. '''

        viewer = self.configset.get("MISC", "html_viewer")
        os.system(getwumappyhelp(viewer))

    def geophpypdfhelp(self):
        ''' Start pdf user guide for  geophpy. '''

        viewer = self.configset.get("MISC", "pdf_viewer")
        os.system(getgeophpyhelp(viewer, 'pdf'))

    def geophpyhtmlhelp(self):
        '''
        Start html user guide for geophpy. '''
        viewer = self.configset.get("MISC", "html_viewer")
        os.system(getgeophpyhelp(viewer))

    def font(self):
        '''
        Edits Font Settings
        '''

        qfontdlg = QFontDialog(self.asciiset.font, self.wid)
        qfontdlg.setFont(self.asciiset.font)
        qfontdlg.setGeometry(self.geometry().left(), self.geometry().top(), qfontdlg.geometry().width(), qfontdlg.geometry().height())
        qfontdlg.show()
        qfontdlg.exec()
        font = qfontdlg.selectedFont()

        if qfontdlg.result() == QDialog.Accepted:
            self.asciiset.font = font
            self.asciiset.fontname = font.family()
            self.asciiset.fontsize = font.pointSize()
            self.wid.setFont(font)                              # sets the font before updating menu bar

                                                                # updates configuration file
            self.configset.set('ASCII', 'fontname', self.asciiset.fontname)
            self.configset.set('ASCII', 'fontsize', str(self.asciiset.fontsize))
                                                                # updates menu bar with new language or font
            self.menubar.update()
                                                                # updates all data set windows
            self.fillingwindow()

            for datasetwindow in self.datasetwindowslist:
                datasetwindow.menubar.update()
                                                                # updates all geopos set windows
            for geopossetwindow in self.geopossetwindowslist:
                geopossetwindow.menubar.update()

    def exit(self):
        '''
        Exits wumappy application
        '''
        for datasetwindow in self.datasetwindowslist:           # exits all data set windows
            datasetwindow.wid.close()
        for geopossetwindow in self.geopossetwindowslist:       # exits all geo pos set windows
            geopossetwindow.wid.close()
        self.configset.save()                                   # saves configuration file
        self.wid.close()                                        # exits current window

# Documentation path
##help_path = os.path.join(__file__, 'help')
help_path = os.path.join(lib_dir, 'help')
htmlhelp_filename = os.path.abspath(os.path.join(help_path, 'html', 'index.html'))
pdfhelp_filename = os.path.abspath(os.path.join(help_path, 'pdf', 'WuMapPy.pdf'))

def getwumappyhelp(viewer='none', doctype='html'):
    '''
    To get help documentation of WuMapPy

    Parameters:

    :viewer:

    :doctype: type of help needed, 'html' or 'pdf'.

    Returns:

    :helpcommand: application to start followed by pathname and filename of the 'html' or 'pdf' help document.

    '''

    path_selector = {
        'pdf' : pdfhelp_filename,
        'html' : htmlhelp_filename
        }

    pathfilename = path_selector[doctype]

##    if doctype == 'pdf':
##       pathfilename = pdfhelp_filename
##
##    else:
##       pathfilename = htmlhelp_filename

    if viewer == 'none':           # start automatically the best application
        helpcommand = pathfilename

    else:
        helpcommand = viewer + " " + pathfilename

    return helpcommand



def main():
    '''Parse command-line arguments and execute WuMapPy command.'''

    parser = argparse.ArgumentParser(prog='%s' % SOFTWARE,
                                     description='%s' % DESCRIPTION)
    parser.add_argument('--version', action='version',
                        version='%s version %s' % (SOFTWARE, VERSION),
                        help='Print %s’s version number and exit.' % SOFTWARE)

    wumappy = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("Cleanlooks")) # cleanlooks correct som bugs in sliders
    gui = WuMapPyGui()

    sys.exit(wumappy.exec_())



if __name__ == '__main__':
    main()

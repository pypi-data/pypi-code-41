# -*- coding: utf-8 -*-
'''
    wumappy.gui.common.cartodlgbox
    ------------------------------

    Common dialog box management with cartography object.

    :copyright: Copyright 2014-2019 Lionel Darras, Philippe Marty, Quentin Vitale and contributors, see AUTHORS.
    :license: GNU GPL v3.

'''

from __future__ import absolute_import
import os
import numpy as np

#from Qt import QtCore, QtWidgets # Qt.py is a shim around all Qt bindings
from Qt import __binding__
from Qt.QtCore import *
from Qt.QtGui import *
from Qt.QtWidgets import *

if __binding__ in ('PyQt5', 'PySide2'):
    is_qt5 = True
    is_qt4 = not is_qt5
elif __binding__ in ('PyQt4', 'PySide'):
    is_qt4 = True
    is_qt5 = not is_qt4

#from PySide import QtCore, QtGui
# Trying to handle both PySide (Qt4) and PySide2 (Qt5)
##try:
##    from PySide import QtCore, QtGui
##    from PySide.QtGui import *
##    from PySide.QtCore import *
##    is_qt4 = True
##    is_qt5 = not is_qt4
##
##except ImportError:
##    from PySide2 import QtCore, QtGui #, QtWidgets
##    from PySide2.QtGui import *
##    from PySide2.QtCore import *
##    from PySide2.QtWidgets import *
##    is_qt5 = True
##    is_qt4 = not is_qt5

if is_qt4:
    from matplotlib.backends.backend_qt4agg import (
        NavigationToolbar2QT as NavigationToolbar,
        FigureCanvasQTAgg as FigureCanvas)
else:
    from matplotlib.backends.backend_qt5agg import (
        NavigationToolbar2QT as NavigationToolbar,
        FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#from geophpy.dataset import *

#from win32api import GetSystemMetrics
#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
#from matplotlib.figure import Figure

### Still under construction
## from matplotlib examples
###
##class MplCanvas(FigureCanvas):
##    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
##
##    def __init__(self, parent=None, width=5, height=4, dpi=100):
##        fig = Figure(figsize=(width, height), dpi=dpi)
##        self.axes = fig.add_subplot(111)
##
##        self.compute_initial_figure()
##
##        FigureCanvas.__init__(self, fig)
##        self.setParent(parent)
##
##        FigureCanvas.setSizePolicy(self,
##                                   QtWidgets.QSizePolicy.Expanding,
##                                   QtWidgets.QSizePolicy.Expanding)
##        FigureCanvas.updateGeometry(self)
##
##    def compute_initial_figure(self):
##        pass

class QGraphic(QWidget):
    ''' Class to display Matplotlib figures in QtWidget.

    (inspired from PyQtGraph canvas)

    '''

    clicked = Signal(QMouseEvent)

    def __init__(self, parent=None):
        super(QGraphic, self).__init__()
        #QWidget.__init__(self)

        # Creating mpl figure & canvas
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setParent(parent)

        self.canvas.setSizePolicy(QSizePolicy.Expanding,
                                  QSizePolicy.Expanding)

        # Connection to mpl mouse event

        ## Needed for mouse modifiers (x,y, <CTRL>, ...):
        ##    Key press events in general are not processed unless you
        ##    "activate the focus of Qt onto your mpl canvas"
        ## http://stackoverflow.com/questions/22043549/matplotlib-and-qt-mouse-press-event-key-is-always-none
##        self.canvas.setFocusPolicy( Qt.ClickFocus )
##        self.canvas.setFocus()
##        self.canvas.updateGeometry()

        # Connection to mpl mouse event
        self.canvas.mpl_connect('button_press_event', self.mousePressEvent)
        self.canvas.mpl_connect('motion_notify_event', self.mouseMoveEvent)

        # figure toolbar
#        self.toolbar = NavigationToolbar(self.canvas, self)

        # Layout
        self.layout = QVBoxLayout()  # implements Layout to display canvas inside
 #       self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.setMinimumSize(1, 1)

    def getFigure(self):
        return self.fig

    def draw(self):
        self.canvas.draw()

    def clearLayout(self):
        ''' clear layout '''

        while self.layout.count() > 0:
            item = self.layout.takeAt(0)

            if not item:
                continue

            w = item.widget()
            if w:
                w.deleteLater()

    def update(self, fig=None):
        ''' Updating embeded figure.'''

        if fig is not None:
            # fig is close to prevenent too many figure retained
            # in the pyplot figure manager
            self.fig = fig
            plt.close(fig)

        self.canvas = FigureCanvas(self.fig)
        self.clearLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.draw()

    def getPosition(self, event):
        x = event.xdata
        y = event.ydata
        return x, y
    
    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        return
        QMouseEvent.globalPos()
        # Left click
        if event.button==1:
            x, y = self.getPosition(event)
            QToolTip.showText(QMouseEvent.globalPos(), "(%.02f,%.02f)"%(x, y))

        # Right click
        if event.button==2:
            x, y = self.getPosition(event)
            QToolTip.showText(QMouseEvent.globalPos(), "(%.02f,%.02f)"%(x, y))


class Item():
    id = None       # item identifiant
    type = None     # item type, 'CheckBox', 'ComboBox', 'SpinBox', 'DoubleSpinBox', 'Label', 'ValidButton', 'CancelButton', 'MiscButton' ...
    init = None     # item init() function
    update = None   # item update() function

class QCarto(QLabel):
    '''
    Class to display Images in CartoDlgBox.
    '''

    clicked = Signal(QMouseEvent)

    def __init__(self, x_min=None, x_max=None, x_gridding_delta=None, y_min=None, y_max=None, y_gridding_delta=None):
        super(QCarto, self).__init__()
        self.x_min = x_min
        self.x_max = x_max
        self.x_gridding_delta = x_gridding_delta
        self.y_min = y_min
        self.y_max = y_max
        self.y_gridding_delta = y_gridding_delta
        self.width = None
        self.height = None
        
        if ((x_min is None) or (x_max is None) or (x_gridding_delta is None) or (y_min is None) or (y_max is None) or (y_gridding_delta is None)):
            self.availablepositionflag = False
        else:
            self.availablepositionflag = True
            

    def getPosition(self, event):
        pos = event.pos()
        x = self.x_min + (pos.x() * (self.x_max - self.x_min))/self.width
        y = self.y_max - (pos.y() * (self.y_max - self.y_min))/self.height
        return x, y
        

    def event(self, event):
        if ((event.type() == QEvent.ToolTip) and self.availablepositionflag and (self.width!=None) and (self.height!=None)):
            ###
            w, h = self.getSize()
            self.setSize(w, h)
            ###
            x, y = self.getPosition(event)
            QToolTip.showText(event.globalPos(), "(%.02f,%.02f)"%(x, y))
        return super(QCarto, self).event(event)


    ###
    def getSize(self):
        w = self.geometry().width()
        h = self.geometry().height()
        return w, h 
    ###

    def setSize(self, w, h):
        self.width = w
        self.height = h

    def mousePressEvent(self, event):
        if (event.buttons() & Qt.LeftButton):
            if (self.update != None):
                ###
                w, h = self.getSize()
                self.setSize(w, h)
                ###
                x, y = self.getPosition(event)
                self.update(x, y)



#---------------------------------------------------------------------------#
# Display Carto Dialog Box Object                                           #
#---------------------------------------------------------------------------#
class CartoDlgBox(QDialog):
    '''
    Class to create a dialogbox containning multiple widgets directly from
    an item list.

    The item list must firt contain all the groupbox properties (if any) and
    then the other wigdet properties.

    Groupbox properties must be in the following order:
    # col: 0,    1    ,    2   ,    3   ,      4     ,   5     ,     6     ,      7      ,               8              ,    9    ,    10   , 11
    #  [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ORIENTATION (0=Vert, 1=Horiz), ROW_SPAN, COL_SPAN, GROUP_TAB_TYPE]

        GROUP_TAB_NUM = 2  --> classic GroupBox
        GROUP_TAB_NUM != 2 --> GroupBox as tab in the group of tab number GROUPBOX_IDX 
    
    Widget properties must be in the following order
    # col: 0,    1    ,    2   ,    3   ,      4     ,   5     ,     6     ,      7      ,    8    ,    9
    #  [TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROW_SPAN, COL_SPAN]

    Example:
    

    (for GB) 0=Vert 1=Hori , COLL SPAN , ROW SPAN

    items_list = [ \
        ## GROUPBOX properties #################################################
        #[TYPE, LABEL_ID, ROW_IDX, COL_IDX, ISAVAILABLE, INIT_FUN, UPDATE_FUN, GROUPBOX_IDX, ROWS_PAN, COL_SPAN]
        ['GroupBox', 'FILEFORMATOPT_ID', 0, 0, False, None, None, 0, 0, 1, 1, 0],


    
    '''

    def __init__(self, title, parent, it_list):
        '''
        Parameters :
        :title: title of dialog box
        :parent: parent windows object
        :it_list: list of items to add in the dialog box.
            [type, label, col_index, isavailable, init, update],... , with :
            :type: item type, 'CheckBox', 'ComboBox', 'SpinBox', 'Label', 'DoubleSpinBox', 'Slider', 'Carto', 'ValidButton', 'CancelButton', 'MiscButton', ...
            :label: item label.
            :col_index: index of the column to display item, 0,1, ...
            :isavailable: True if item is available, False if not.
            :init: initialisation function for item init(), 'None' if no function.
            :update: update function for item update(), 'None' if no function.

        '''

        super(CartoDlgBox, self).__init__()

        group_box_tab = []  # GROUPBOX list
        group_tab = []  # tabWidget list
        layout_tab = []  # layout list

        self.asciiset = parent.asciiset
        self.icon = parent.icon
        self.setFont(self.asciiset.font)
        self.items_list = []

        layout = QGridLayout()                # builds the main layout
                                                    # the main layout will be composed by 2 layouts as columns

        change_resolution = parent.configset.getboolean('MISC', 'changeresolutionflag')  # Tab flag (Vs all same layout)

        parent.wid = self

        self.setWindowTitle(title)                  # sets the windows title
        self.setWindowIcon(self.icon)               # sets the wumappy logo as window icon

        
        # Layout total number of  columns ######################################
        a = 0
        col_nb = 0                                  # number of columns        
        for it in it_list:
            col_index = it[3]
            if ((1+col_index) > col_nb):
                col_nb = 1 + col_index
            a += 1
         
        # Creating layout widgets from the widget list
        for it in it_list:
            # current widget properties ########################################
            item = Item()
            item.type = it[0]
            label = self.asciiset.getStringValue(it[1])
            row_index = it[2]
            col_index = it[3]
            isavailable = it[4]  # not used ?
            item.init = it[5]  # item init funtion
            item.update = it[6]  # item update funtion

            isValid = True

            # GroupBox Widgets creation ########################################
            if item.type == 'GroupBox':

                    # Tab mode display
                    if change_resolution:
                        # Adding GroupBox as a Tab in the QTabWidget number it[11]
                        if it[11] != 2:
                            # Creating a new TabGroup (QTabWidget)
                            if len(group_tab) == it[11]:
                                group_tab.append(QTabWidget())
                                layout.addWidget(group_tab[-1], row_index, col_index)

                            # Adding a Tab to the TabGroup
                            item.id = QWidget()
                            group_tab[it[11]].addTab(item.id, label)

                        # Adding a classic Groupbox
                        else:
                            item.id = QGroupBox(label)

                        item.id.setFont(self.asciiset.font)
                        group_box_tab.append(item.id)
                        layout_tab.append(QGridLayout())
                        group_box_tab[-1].setLayout(layout_tab[-1])
                        
                        # ?????
                        if (it[11] == 1 or it[11] == 0):
                            layout.addWidget(group_tab[-1], 0, 0, it[9], it[10])
                        else:
                            layout.addWidget(item.id, row_index, col_index, it[9], it[10])

                    # Classic grid layout display
                    else:
                        item.id = QGroupBox(label)
                        item.id.setFont(self.asciiset.font)
                        group_box_tab.append(item.id)
                        layout_tab.append(QGridLayout())
                        item.id.setLayout(layout_tab[-1])
                        layout.addWidget(item.id, row_index, col_index, it[9], it[10])

            # Other Widget items (CheckBox, ComboBox...) creation ##############
            elif (item.type == 'CheckBox'):
##            if (item.type == 'CheckBox'):
                item.id = QCheckBox(label)
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'ComboBox'):
                item.id = QComboBox()
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'SpinBox'):
                item.id = QSpinBox()
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'DoubleSpinBox'):
                item.id = QDoubleSpinBox()
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'Slider'):
                item.id = QSlider()

            elif item.type == 'Radio':
                item.id = QRadioButton(label)
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'Label'):
                item.id = QLabel(label)
                item.id.setFont(self.asciiset.font)
                item.id.setWordWrap(True)

            elif (item.type == 'TextEdit'):
                item.id = QTextEdit(label)
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'LineEdit'):
                item.id = QLineEdit(label)
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'Image'):
                try:
                    item.id = QCarto(parent.dataset.info.x_min, parent.dataset.info.x_max, parent.dataset.info.x_gridding_delta, parent.dataset.info.y_min, parent.dataset.info.y_max, parent.dataset.info.y_gridding_delta)
                except:
                    item.id = QCarto()
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'Graphic'):
                try:
                    item.id = QGraphic()
                    #item.id = Mpwidget()
                    
                except:
                    item.id = QGraphic()
                    #item.id = Mpwidget()
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'Table'):
                item.id = QTableWidget()
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'ValidButton'):
                item.id = QPushButton(label)
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'CancelButton'):
                item.id = QPushButton(label)
                item.id.setFont(self.asciiset.font)

            elif (item.type == 'MiscButton'):
                item.id = QPushButton(label)
                item.id.setFont(self.asciiset.font)


            # GroupBox Widgets
##            elif (item.type == 'GroupBox'):
##                    if (change_resolution):
##                        if (it[11] != 2):
##                            if len(group_tab) == it[11]:
##                                group_tab.append(QTabWidget())
##                                layout.addWidget(group_tab[-1], row_index, col_index)
##                            item.id = QWidget()
##                            group_tab[it[11]].addTab(item.id, label)
##                        else:
##                            item.id = QGroupBox(label)
##                        item.id.setFont(self.asciiset.font)
##                        group_box_tab.append(item.id)
##                        layout_tab.append(QGridLayout())
##                        group_box_tab[-1].setLayout(layout_tab[-1])
##                        if (it[11] == 1 or it[11] == 0):
##                            layout.addWidget(group_tab[-1], 0, 0, it[9], it[10])
##                        else:
##                            layout.addWidget(item.id, row_index, col_index, it[9], it[10])
##                    else:
##                        item.id = QGroupBox(label)
##                        item.id.setFont(self.asciiset.font)
##                        group_box_tab.append(item.id)
##                        layout_tab.append(QGridLayout())
##                        item.id.setLayout(layout_tab[-1])
##                        layout.addWidget(item.id, row_index, col_index, it[9], it[10])
            else:
                isValid = False

            # Initialisation of init signals and functions #####################
            if ((isValid == True) and (col_index >= 0) and (col_index < col_nb)):
                self.items_list.append(item)
                if (col_index == (col_nb - 1)):
                    col_index = 0

                if item.init is not None:
                    item.id = item.init(item.id)

                if (item.type == 'CheckBox'):
                    if (item.update is not None):
                        item.id.stateChanged.connect(item.update)

                elif (item.type == 'ComboBox'):
                    if (item.update is not None):
                        item.id.currentIndexChanged.connect(item.update)

                elif (item.type == 'SpinBox'):
                    if (item.update is not None):
                        item.id.valueChanged.connect(item.update)

                elif (item.type == 'DoubleSpinBox'):
                    if (item.update is not None):
                        item.id.valueChanged.connect(item.update)

                elif (item.type == 'Slider'):
                    if item.update is not None:
                        #item.id.sliderPressed.connect(item.update)  # updates when slider is presed
                        #item.id.sliderReleased.connect(item.update)  # updates when slider is released
                        item.id.sliderMoved.connect(item.update)  # updates when slider is moved


                elif item.type == 'LineEdit':
                    if item.update is not None:
                        item.id.editingFinished.connect(item.update)                    
                elif item.type == 'Radio':
                    if item.update is not None:
                        item.id.toggled.connect(item.update)
                elif (item.type == 'Image'):
                    item.id.update = item.update
                elif (item.type == 'ValidButton'):
                    item.id.clicked.connect(self.valid)
                elif (item.type == 'CancelButton'):
                    item.id.clicked.connect(self.cancel)
                elif (item.type == 'MiscButton'):
                    if (item.update != None):
                        item.id.clicked.connect(item.update)                    

            # Managing Item in the layout ######################################
            # No Groupbox in the main layout
            if not group_box_tab:
                layout.addWidget(item.id, row_index, col_index)

            # Label Item  
            elif (item.type == 'Label'):
                # Specified row and column span
                ###
                if len(it)==10:
                    row_span = it[8]
                    col_span = it[9]
                    layout_tab[it[7]].addWidget(item.id, row_index, col_index, row_span, col_span)

                # Default row and column span
                else:
                    layout_tab[it[7]].addWidget(item.id, row_index, col_index, 1, 1)
                ###

                #layout_tab[it[7]].addWidget(item.id, it[2], it[3], 1, 1)

            # Groupbox Item
            ## Already taken care of at the beginning

            # Other Item
            elif (item.type != 'GroupBox'):
                # Specified row and column span
                if len(it)==10:
                    layout_tab[it[7]].addWidget(item.id, it[2], it[3], it[8], it[9])
                    ###
                    #row_span = it[8]
                    #col_span = it[9]
                    #layout_tab[it[7]].addWidget(item.id, row_index, col_index, row_span, col_span)
                    ###

                # Default row and column span
                else:
                    layout_tab[it[7]].addWidget(item.id, it[2], it[3], 1, 1) # ajout dun col span ici

        self.update()
        #layout.setSizeConstraint(QLayout.SetFixedSize)    # to not authorize size modification
        ###
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        ###

        # Resize handle
##        col_index = layout.columnCount()
##        row_index = layout.rowCount()
##        sizegrip = QSizeGrip(self)
##        layout.addWidget(sizegrip, row_index, col_index)
        layout.addWidget(QSizeGrip(self), Qt.AlignBottom, Qt.AlignRight)
        ###
        self.setLayout(layout)
        ###
        self.setSizePolicy(QSizePolicy.Expanding,
                             QSizePolicy.Expanding)
        ###
        

    def valid(self):
        ''' Close the dialog box. '''
        self.accept()
        self.close()        

    def cancel(self):
        ''' Closes the dialog box. '''
        self.close()

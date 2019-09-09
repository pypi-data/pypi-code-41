'''
 Copyright (c) 2019, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt5.QtCore as qtCore
from PyQt5.QtWidgets import QVBoxLayout, QSlider, QLabel, QSplitter, \
    QWidget, QMenu, QAction
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRectF
from minixs import METHOD_ENTER_STR
import numpy as np
from PIL import Image
from pyqtgraph import ImageItem, ScatterPlotItem, functions
from pyqtgraph import GraphicsLayoutWidget
import os
import logging
from minixs.gui.qthelpers.qtfilterview import REGISTRY
from pyqtgraph.widgets.HistogramLUTWidget import HistogramLUTWidget
from PyQt5.Qt import QRadioButton, QGroupBox, QPushButton, QCheckBox, QComboBox,\
    QHBoxLayout, QMessageBox
from minixs.constants import DIRECTION_NAMES
from minixs.filter import MIN_VISIBLE_FILTER, MAX_VISIBLE_FILTER,\
    get_filter_by_name
from pyqtgraph.graphicsItems.ROI import RectROI
from matplotlib import cm
from minixs.gui.qthelpers import qtfilterview

logger = logging.getLogger(__name__)

FIND_CRYSTAL_SIGNAL = "findCrystals"
SHOW_CRYSTAL_SIGNAL = "showCrystals"
VIEW_CHOICE_CHANGED_SIGNAL = "viewChoiceChanged"
NO_EXPOSURES_LABEL = "No Exposures Loaded"
CALIBRATION_MATRIX_LABEL = "CalibrationMatrix"
EXPOSURE_LABEL_TEMPLATE = "%d/%d %s %f"
CHECK_BOX_KEY = 'checkBox'
VALUE_KEY = 'value'

class ImageViewQt(QWidget):
    '''
    classdocs
    '''
    findCrystals = pyqtSignal(name=FIND_CRYSTAL_SIGNAL)
#     showCrystals = pyqtSignal(bool, name=SHOW_CRYSTAL_SIGNAL)

    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        super(ImageViewQt, self).__init__(*args, **kwargs)
        layout = QVBoxLayout()
        hSplitter = QSplitter()
        
        self.filters = FilterBox()
        self.imageView = ImageBox()
        self.matrixView = CalibrationMatrixBox()
        self.tools = ToolBox()
        self.filters.filterChanged[object].connect(self.handleImageFilterChanged)

        self.imageBox=QWidget()
        imageBoxLayout = QHBoxLayout()
        imageBoxLayout.addWidget(self.imageView)
        self.imageBox.setLayout(imageBoxLayout)
        
        hSplitter.addWidget(self.filters)
        hSplitter.addWidget(self.imageBox)
        
        hSplitter.addWidget(self.tools)
        
        self.tools.findCrystals.connect(self.handleFindCrystals)
        self.tools.calibrationRadioButton.toggled.connect(
            self.handleViewChangeToCalibration)
        self.tools.exposureRadioButton.toggled.connect(
            self.handleViewChangeToExposure)
        self.tools.showCrystals[bool].connect(self.imageView.showCrystals)
        
        layout.addWidget(hSplitter)
        self.calibrateButton = QPushButton("Calibrate")
        layout.addWidget(self.calibrateButton)
        self.setLayout(layout)
        
    def deleteImages(self, rows):
        logger.debug(METHOD_ENTER_STR, (rows,))
        self.imageView.deleteImages(rows)
        
    def loadImages(self, filenames, energies):
        logger.debug(METHOD_ENTER_STR % ((filenames,energies),))
        self.imageView.loadImages(filenames, energies)
        self.filters.setEnabled(True)
        
    def handleImageFilterChanged(self, filterObj):
        logger.debug(METHOD_ENTER_STR % filterObj)
        logger.debug("filter %s enabled: %s" % (filterObj.text(), filterObj.filterEnabled()))
        logger.debug("filter %s value: %s" % (filterObj.text(), filterObj.getValue()))
        if self.imageView.imageStack.size == 0:  # Cannot do anything with no data.
            return
        self.updateImageDisplayFilters()
        
    def updateImageDisplayFilters(self):
        imageDisplayFilters = self.filters.getImageDisplayFilters()
        self.imageView.applyFilters(self.filters.getFilters())
        self.imageView.applyImageFilters(imageDisplayFilters)
        
    def handleFindCrystals(self):
        self.findCrystals.emit()
        
    def handleViewChangeToExposure(self, checked):
        logger.debug(METHOD_ENTER_STR % checked)
        if checked:
            imageBoxLayout = self.imageBox.layout()
            self.matrixView.setVisible(False)
            imageBoxLayout.removeWidget(self.matrixView)
            self.imageView.setVisible(True)
            imageBoxLayout.addWidget(self.imageView)
            imageBoxLayout.update()

    def handleViewChangeToCalibration(self, checked):
        logger.debug(METHOD_ENTER_STR % checked)
        if checked:
            imageBoxLayout = self.imageBox.layout()
            self.imageView.setVisible(False)
            imageBoxLayout.removeWidget(self.imageView)
            self.matrixView.setVisible(True)
            imageBoxLayout.addWidget(self.matrixView)
            imageBoxLayout.update()
        
class FilterBox(QWidget):
    filterChanged = pyqtSignal(object, name="filterChanged")
    def __init__(self, *args, **kwargs):
        super(FilterBox, self).__init__(*args, **kwargs)
        self.views = {}
        filters = REGISTRY
        self.filterWidgets = []
        logger.debug("Filters: %s" % filters)
        layout = QVBoxLayout()
        for dfilter in filters:
            filterWidget = dfilter[1](filter=dfilter[0]())
            layout.addWidget(filterWidget)
            filterWidget.filterChanged[object].connect(self.filterStateChanged)
            self.filterWidgets.append(filterWidget)
            self.views[dfilter[0]] = filterWidget
        label = QLabel("Dispersive Direction")
        self.dispersiveDirection = QComboBox()
        self.dispersiveDirection.addItems(DIRECTION_NAMES)
        hLayout = QHBoxLayout()
        hLayout.addWidget(label)
        hLayout.addWidget(self.dispersiveDirection)
        layout.addLayout(hLayout)
        self.setLayout(layout)
        
        self.setEnabled(False)
    
    def filterStateChanged(self, filterObj):
        self.filterChanged.emit(filterObj)

    def _getDisplayFilterVals(self, filterWidget):
        return {CHECK_BOX_KEY: filterWidget.filterEnabled(),
                VALUE_KEY: filterWidget.getValue()}
                    
    def getFilters(self):
        filters = []
        for fw in self.filterWidgets:
            filters.append((fw.filter.name, fw.filterEnabled(), fw.getValue()))
        return filters
            
    def _getFilterDefaults(self, fltr):
        valStr = ""
        
        if hasattr(fltr, 'default_name'):
            valStr = fltr.val_to_str(fltr.default_val)
        val = fltr.str_to_val(valStr)
          
        enabled = False
        if hasattr(fltr, 'default_enabled'):
            enabled = fltr.default_enabled
        
        return (enabled, val)
            
        
        
    def getImageDisplayFilters(self):
        displayFilters = {}
        for dfilter in self.filterWidgets:
            logger.debug("DisplayFilter %s" % dfilter)
            if dfilter.filter.name == MIN_VISIBLE_FILTER:
                displayFilters[MIN_VISIBLE_FILTER] = self._getDisplayFilterVals(dfilter)
            elif  dfilter.filter.name == MAX_VISIBLE_FILTER:
                displayFilters[MAX_VISIBLE_FILTER] = self._getDisplayFilterVals(dfilter)
        return displayFilters
        
    def setFilters(self, filters):
        logger.debug(METHOD_ENTER_STR)
        fmap = {}
        for f in filters:
            fmap[f.__class__] = f
            
        for ftype, view_class in qtfilterview.REGISTRY:
            if ftype in fmap:
                enabled = True
                val = fmap[ftype].get_val()
            else:
                enabled, val = self._getFilterDefaults(ftype)
                enabled = False
            self.views[ftype].filterEnableChanged(enabled)
            if val is not None:
                self.views[ftype].setValue(val)
        
        
class ImageBox(QWidget):
    '''
    Widget box to display the image stack, & slider to allow switching 
    which image is displayed
    '''    
    allImagesDeleted = pyqtSignal(name="allImagesDeleted")
    
    def __init__(self, *args, **kwargs):
        super(ImageBox, self).__init__(*args, **kwargs)
        self.lastMousePosition = [0, 0]
        self.handlersConnected = False
        self.images = []
        self.imageEnergies = []
        self.imageStack = None
        self.rois = []
        self.filters = []
        
        layout = QVBoxLayout()
        self.imageLabel=QLabel(NO_EXPOSURES_LABEL)
        layout.addWidget(self.imageLabel)
        graphicsWidget = GraphicsLayoutWidget()
        self.viewBox = graphicsWidget.addViewBox()
        self.viewBox.setAspectLocked(True)
        self.updateMenu()
        self.imageView = ImageItem( border={'color':'333'})
        self.imageView.setOpts(axisOrder='row-major')
        self.viewBox.setVisible(False)
        self.imageNumber = -1
        self.fitPointsView = ScatterPlotItem()
        
        
        self.viewBox.addItem(self.imageView)
        self.viewBox.show()
        layout.addWidget(graphicsWidget)
        self.slider = QSlider(qtCore.Qt.Horizontal)
        layout.addWidget(self.slider)
        
        self.histWidget = HistogramLUTWidget(image=self.imageView)
        colormap = cm.get_cmap("Greys_r")
        colormap._init()
        lut = (colormap._lut *255).view(np.ndarray)
        self.imageView.setLookupTable(lut)
        self.histWidget.item.setImageItem(self.imageView)
        #layout.addWidget(self.histWidget)
     
        self.setLayout(layout)


    def _addDecoratedROI(self, position, size):
        imageSize = list(self.imageStack[0].shape)
        bounds = QRectF(0, 0, imageSize[1], imageSize[0])
        roi = RectROI(position, size,\
                      maxBounds=bounds,
                      removable=True, movable=True,
                      sideScalers=True)
        roi.sigRemoveRequested.connect(self.removeROI)
        roi.addScaleHandle([0,.5], [1,.5])
        roi.addScaleHandle([.5,0], [.5,1])
        self.rois.append(roi)
        self.viewBox.addItem(roi)
        
    def addROI(self):
        '''
        Add a single ROI at [0,0] & size[50, 50].  This is 
        meant to add an ROI that will be moved to a desired location
        by the user.
        '''
        if self.imageStack is not None:
            imageSize = list(self.imageStack[0].shape)
            logger.debug("imageSize %s" % (imageSize,))
            self._addDecoratedROI(self.lastMousePosition, [50, 50])
        else:
            self._addDecoratedROI(self.lastMousePosition, [50, 50])

    def addROIs(self, rects):
        '''
        Add ROIs of size & location determined by the list
        of rects passed in
        '''
        for rect in rects:
            logger.debug("rect %s" % rect)
            position = rect[0]
            size = [rect[1][0] - rect[0][0],\
                                    rect[1][1] - rect[0][1]]
            self._addDecoratedROI(position, size)
            
    
    def applyFilters(self, filters):
        '''
        Apply filters as defined on the current image.  These filters will 
        maks out data based on criteria specified in the filters.
        '''
        logger.debug(METHOD_ENTER_STR % (filters,))
        self.filters = filters
        filteredData = self.getFilteredData()
        imageLevels = self.imageView.getLevels()
        logger.debug("Display image %s" % (imageLevels,))
        logger.debug("filtered Data min/max %s/%s" % (filteredData.min(), filteredData.max()))
        if (filteredData.min() != filteredData.max()):
            self.imageView.setImage(filteredData, autoLevels=False)
            self.imageView.border = functions.mkPen({'color': '333'})
            self.viewBox.update()
        else:         # pyqt graph does not crashes if image is completely flat
            self.imageView.setImage(None)
            self.imageView.border = functions.mkPen({'color': 'F00'})
            self.viewBox.update()

    def applyImageFilters(self, filters):
        '''
        Use the filter values for Min Visible and
        Max Visible to scale the image by setting the level on the 
        current image.
        '''
        logger.debug(METHOD_ENTER_STR % (filters,))
        if MIN_VISIBLE_FILTER not in filters.keys():
            logger.warning("Minimum Visible Filter is missing")
            return
        if MAX_VISIBLE_FILTER not in filters.keys():
            logger.warning("Maximum Visible Filter is missing")
            return
        minRange = 0
        maxRange = 1000
        imageNumber = self.slider.value()
        logger.debug("Filters %s" % filters)
        if filters[MIN_VISIBLE_FILTER][CHECK_BOX_KEY]:
            minRange = filters[MIN_VISIBLE_FILTER][VALUE_KEY]
        else:
            minRange = np.min(self.imageStack[imageNumber,:,:])
        if filters[MAX_VISIBLE_FILTER][CHECK_BOX_KEY]:
            maxRange = filters[MAX_VISIBLE_FILTER][VALUE_KEY]
        else:
            maxRange = np.min(self.imageStack[imageNumber,:,:])
        self.histWidget.item.setLevels(minRange, maxRange)
        self.imageView.setLevels((minRange,maxRange))

    def clearImages(self):
        '''
        if the images or energies are cleared then clear the imageView image
        and change the imageLabel.  Alsp  clear out the image names, imageStack
        and Energu List.
        '''
        self.imageLabel(NO_EXPOSURES_LABEL)
        self.imageView.setImage(None)
        
    def connectDataSignals(self):
        if not self.handlersConnected and len(self.images) >0:
            self.histWidget.item.sigLevelChangeFinished.connect( \
                                    self.handleSigLevelChangeFinished)
            self.histWidget.item.sigLookupTableChanged.connect( \
                                    self.handleSigLookupTableChanged)
#                 self.histWidget.item.sigLevelsChanged.connect( \
#                                         self.handleSigLevelsChanged)
            self.imageView.scene().sigMouseMoved.connect( \
                                    self.handleMouseMove)
            self.slider.valueChanged.connect(self.setCurrentImage)
            self.handlersConnected = True
            
        
        
    def deleteAllImages(self):
        imageRows = range(len(self.images))
        self.deleteImages(reversed(imageRows))
        self.allImagesDeleted.emit()
        
    def deleteImages(self, rows):
        '''
        delete a set of images from the display,  This is triggerd by the 
        delete rows from the exposure selector.
        '''
        logger.debug(METHOD_ENTER_STR % (rows,))
        self.disconnectDataSignals()
        for row in rows:
            logger.debug("Removing Row %s" % row)
            if len(self.images) > 0:
                self.images.remove(self.images[row])
                self.imageStack = np.delete(self.imageStack, row, axis=0 )
            if len(self.imageEnergies) > 0:
                self.imageEnergies.remove(self.imageEnergies[row])
            if len(self.images) > 0:
                self.setCurrentImage(0)
                logger.debug("Setting maximum value for the slider to %s" %
                         (self.imageStack.shape[0] - 1))
                self.slider.setMaximum(self.imageStack.shape[0] - 1)
                self.connectDataSignals()
            else:
                self.setCurrentImage(None)
                self.slider.setMaximum(self.slider.minimum())
                self.disconnectDataSignals()
                
    def disconnectDataSignals(self):
        '''
        Disconnect signals related to selecting or changing data, ranges, etc
        while data is being loaded, deleted, modified etc to avoid problems.
        '''
        if self.handlersConnected:
            self.histWidget.item.sigLevelChangeFinished.disconnect( \
                                        self.handleSigLevelChangeFinished)
            self.histWidget.item.sigLookupTableChanged.disconnect( \
                                        self.handleSigLookupTableChanged)
#             self.histWidget.item.sigLevelsChanged.disconnect( \
#                                         self.handleSigLevelsChanged)
            self.handlersConnected = False
            self.imageView.scene().sigMouseMoved.disconnect( \
                                        self.handleMouseMove)
            self.slider.valueChanged.disconnect(self.setCurrentImage)
        
        
    def getFilteredData(self):
        logger.debug(METHOD_ENTER_STR)
        filteredData = np.copy(self.imageStack[self.imageNumber, slice(None), slice(None)]).astype(np.float64)
        for (name, enabled, val ) in self.filters:
            if enabled:
                try:
                    fltr = get_filter_by_name(name)
                    fltr.set_val(val)
                    fltr.filter(filteredData, 0.0)
                except ValueError:
                    logger.debug("trouble with value change in fillter: %s" \
                                 % fltr)
        return filteredData
        
                       
    def handleMouseMove(self, viewPos):
        '''
        As the mouse is moved over the image show the image possition in the 
        status bar
        '''
#         logger.debug("mouseMoved in %s", object)
        imageNumber = self.slider.value()
        mainWindow = self.window()
        scenePos = self.imageView.mapFromScene(viewPos)
#         logger.debug ("scenePos %s" % ((scenePos,)))
        row, col = int(scenePos.y()), int(scenePos.x())
#         logger.debug ("row, col %s,%s" % (row, col))
        image = self.getFilteredData()
#         logger.debug ("image.shape %s" % ((image.shape,)))
        if (0 <= row < image.shape[0]) and (0 <= col < image.shape[1]):
            mainWindow.statusBar().showMessage("x=%s, y=%s, val=%s" % (col, 
                                                       row, 
                                                       image[row,col]))
            self.lastMousePosition = [col, row]
        else:
            mainWindow.statusBar().showMessage("")

    def handleSigLookupTableChanged(self, obj):
        '''
        '''
        logger.debug(METHOD_ENTER_STR % obj)
        imageNumber = self.slider.value()
        lut = self.histWidget.item.getLookupTable( \
                                    img=self.imageStack[imageNumber,:,:])
        logger.debug("new Lookup Table: %s" % ((lut,)))
          
    def handleSigLevelsChanged(self, obj):
        '''
        Handler for changing the signal levels that define
        the range of data for the image
        '''
        logger.debug(METHOD_ENTER_STR % obj)
        levels = self.histWidget.getLevels()
        logger.debug("new Levels min,max %s, %s" % levels)
  
    def handleSigLevelChangeFinished(self, obj):
        '''
        Handler for when finished changing the signal
        levels that define the limits for the colormap
        used to display the data
        '''
        logger.debug(METHOD_ENTER_STR % obj)
        levels = self.histWidget.getLevels()
        logger.debug("new Levels min,max %s, %s" % levels)

    def loadImages(self, filenames, energies):
        '''
        After images are selected load images into a stack and display the
        first image.
        '''
        logger.debug(METHOD_ENTER_STR, (filenames,))
        self.disconnectDataSignals()
        self.images = filenames
        self.imageEnergies = energies
        #self.imgArray = np.empty()
        self.imageStack = np.array([])
        try:
            if len(filenames) == 0:
                return
            imgs = [Image.open(image, "r") for image in filenames]
            if len(imgs) > 0: 
                logger.debug("images %s" % imgs)
                self.imageStack = np.stack(imgs, axis=0)
#             self.imageStack = np.swapaxes(self.imageStack, 1, 2)
                logger.debug("stack shape %s" % (self.imageStack.shape,))
                self.slider.setMinimum(0)
                self.slider.setMaximum(self.imageStack.shape[0]-1)
                self.setCurrentImage(0)
            else:
                self.slider.setMinimum(0)
                self.slider.setMaximum(self.imageStack.shape[0]-1)
                self.setCurrentImage(None)
                return
            self.connectDataSignals()
            self.viewBox.autoRange(items=[self.imageView,])
            self.imageView.update()
                    
        except IOError as ex:
            msg = str(ex)
            msg = msg + "\nSelected file does not seem to be an image."
            QMessageBox.warning(self, self.tr("Calibrator"), self.tr(msg))
            
    def removeAllROIs(self):
        for ii in reversed(range(len(self.rois))):
            self.removeROI(self.rois[ii])
        
    def removeROI(self, roi):
        '''
        Remove the highlighted ROI
        '''
        roi.sigRemoveRequested.disconnect(self.removeROI)
        self.viewBox.removeItem(roi)
        self.rois.remove(roi)
            
    def replaceXtals(self, rects):
        self.removeAllROIs()
        self.addROIs(rects)
        
        
    @pyqtSlot(int)
    def setCurrentImage(self, imageNumber):
        '''
        As the selected image number changes, display the image and change the imageLabel
        '''
        logger.debug("self.images %s "  % self.images)
        logger.debug("self.imageEnergies %s "  % self.imageEnergies)
        logger.debug("self.imageStack %s "  % self.imageStack)
        
        if not imageNumber is None:
            self.imageLabel.setText(EXPOSURE_LABEL_TEMPLATE % (imageNumber,
                                                     self.imageStack.shape[0] -1,
                                                     os.path.basename(self.images[imageNumber]),
                                                     self.imageEnergies[imageNumber]))
            logger.debug("Image Levels min, max: %s", self.imageView.getLevels())
            colormap = cm.get_cmap("Greys_r")
            colormap._init()
            lut = (colormap._lut *255).view(np.ndarray)
            self.imageView.setLookupTable(lut)
            self.imageNumber = imageNumber
            filteredData = self.getFilteredData()
            self.imageView.setImage(filteredData, autoLevels=False)
            self.viewBox.setVisible(True)
        else:
            self.imageLabel.setText(NO_EXPOSURES_LABEL)
            self.imageView.setImage(image=None)
            self.viewBox.setVisible(False)
#         self.histWidget.item.setImageItem(self.imageStack[imageNumber,:,:])
#         self.histWidget.item.setImageItem(self.imageView)
            
    @pyqtSlot(bool)
    def showCrystals(self, show):
        '''
        Toggle display of ROIs for the crystal boundaries for the 
        image
        '''
        logger.debug(METHOD_ENTER_STR % show)
        for roi in self.rois:
            if show:
                roi.show()
            else:
                roi.hide()

    def setFilters(self,filters):
        self.filters = filters
        
        
    def updateMenu(self):
        '''
        '''
        menu = self.viewBox.menu
        self.roiMenu = QMenu("ROIs")
        
        addROI = QAction("Add ROI", self.roiMenu)
        self.roiMenu.addAction(addROI)
        addROI.triggered.connect(self.addROI)
        removeAllROIs = QAction("Remove All ROIs", self.roiMenu)
        self.roiMenu.addAction(removeAllROIs)
        removeAllROIs.triggered.connect(self.removeAllROIs)
        menu.addMenu(self.roiMenu)
    
class CalibrationMatrixBox(QWidget):
    
    def __init__(self, *args, **kwargs):
        super(CalibrationMatrixBox, self).__init__(*args, **kwargs)
        self.handlersConnected = False
        self.image = None
        self.calImage = None
        self.lastMousePosition = [0,0]
        layout = QVBoxLayout()
        self.imageLabel=QLabel(CALIBRATION_MATRIX_LABEL)
        layout.addWidget(self.imageLabel)
        graphicsWidget = GraphicsLayoutWidget()
        self.viewBox = graphicsWidget.addViewBox()
        self.viewBox.setAspectLocked(True)
        self.imageView = ImageItem( border={'color':'333'})
        self.imageView.setOpts(axisOrder="row-major")
        self.viewBox.addItem(self.imageView)
        self.viewBox.show()
        layout.addWidget(graphicsWidget)
        
        self.histWidget = HistogramLUTWidget(image=self.imageView)
        self.histWidget.item.setImageItem(self.imageView)
#         layout.addWidget(self.histWidget)
        
        self.setLayout(layout)
        self.setVisible(False)
        
    def setImage(self, image):
        '''
        Set the image to be displayed for the calibrated data.
        '''
        if self.handlersConnected:
            self.imageView.scene().sigMouseMoved.disconnect( \
                                        self.handleMouseMove)
            self.handlersConnected = False
        self.image = image
        self.calImage = np.array(image)
#         self.calImage = np.swapaxes(self.calImage, 0, 1)
        nonZeroVals = np.nonzero(self.calImage)
        minVal = np.min(self.calImage[nonZeroVals])
        maxVal = np.max(self.calImage[nonZeroVals])
        # colormap setup
        colormap = cm.get_cmap("jet")
        colormap._init()
        lut = (colormap._lut *255).view(np.ndarray)
        self.imageView.setLookupTable(lut)
        self.imageView.setImage(self.calImage, levels=[minVal,maxVal])
        if not self.handlersConnected:
            self.imageView.scene().sigMouseMoved.connect( \
                                        self.handleMouseMove)
            self.handlersConnected = True

    def handleMouseMove(self, viewPos):
        '''
        As the mouse is moved over the image show the image possition in the 
        status bar
        '''
#         logger.debug("mouseMoved in %s", object)
        mainWindow = self.window()
        scenePos = self.imageView.mapFromScene(viewPos)
#         logger.debug ("scenePos %s" % ((scenePos,)))
        row, col = int(scenePos.y()), int(scenePos.x())
#         logger.debug ("row, col %s,%s" % (row, col))
        image = self.calImage
#         logger.debug ("image.shape %s" % ((image.shape,)))
        if (0 <= row < image.shape[0]) and (0 <= col < image.shape[1]):
            mainWindow.statusBar().showMessage("x=%s, y=%s, val=%s" % (col, 
                                                       row, 
                                                       image[row,col]))
            self.lastMousePosition = [col, row]
        else:
            mainWindow.statusBar().showMessage("")
        
        
class ToolBox(QWidget):
    findCrystals = pyqtSignal(name=FIND_CRYSTAL_SIGNAL)
    showCrystals = pyqtSignal(bool, name=SHOW_CRYSTAL_SIGNAL)
    viewChoiceChanged = pyqtSignal(name=VIEW_CHOICE_CHANGED_SIGNAL)
    def __init__(self, *args, **kwargs):
        super(ToolBox, self).__init__(*args, **kwargs)
        self.rects = []
        layout = QVBoxLayout()
        choices = ["Exposures", "Calibration Matrix"]
        self.radioGroup = QGroupBox("View", maximumHeight=100)
        radioLayout = QVBoxLayout()
        self.exposureRadioButton = QRadioButton(choices[0])
        self.exposureRadioButton.setChecked(True)
        self.calibrationRadioButton = QRadioButton(choices[1])
        radioLayout.addWidget(self.exposureRadioButton, stretch=0)
        radioLayout.addWidget(self.calibrationRadioButton, stretch=0)
        
        self.radioGroup.setLayout(radioLayout)
        findCrystalsButton = QPushButton("Find Crystal Bounds", maximumHeight=50)
        findCrystalsButton.clicked.connect(self.handleFindCrystals)
        findCrystalsButton.setEnabled(False)
        self.showCrystalsCheckBox = QCheckBox("ShowCrystals", maximumHeight = 50)
        self.showCrystalsCheckBox.clicked.connect(self.handleShowCrystals)
        layout.addWidget(self.radioGroup, stretch=0)
        layout.addWidget(findCrystalsButton)
        layout.addWidget(self.showCrystalsCheckBox)
        
        self.setLayout(layout)
        
    def handleFindCrystals(self):
        self.findCrystals.emit()
        
    def handleShowCrystals(self):
        logger.debug(METHOD_ENTER_STR % 
                     self.showCrystalsCheckBox.isChecked())
        self.showCrystals.emit(self.showCrystalsCheckBox.isChecked())
        
        
        
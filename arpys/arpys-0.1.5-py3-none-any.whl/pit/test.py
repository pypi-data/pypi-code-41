from copy import copy

import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore

from imageplot import CursorPlot, CrosshairImagePlot, Scalebar

# Setup UI
app = QtGui.QApplication([])

#window = QtGui.QMainWindow()
widget = QtGui.QWidget()
layout = QtGui.QGridLayout()
widget.setLayout(layout)

ch = CrosshairImagePlot()
ch.crosshair.hpos.sig_value_changed.connect(lambda :print(ch.crosshair.hpos.get_value()))
ch.crosshair.vpos.sig_value_changed.connect(lambda :print(ch.crosshair.vpos.get_value()))

cps = []
for i in range(9) :
    if i%2 :
        cp = CursorPlot()
    else :
        cp = CursorPlot(orientation='horizontal')
    cp.disableAutoRange()
    cp.set_secondary_axis(-2, 3.14)
    ti = pg.TextItem(str(i))
    cp.addItem(ti)
    ti.setPos(0.5, 0.5)
    xscale = cp.getAxis('bottom').range
    data_width = xscale[1] - xscale[0]
    width = cp.frameGeometry().width()
    C = width/data_width
    print(xscale, width)
    cp.set_slider_pen(width=i)
    cps.append(cp)

scalebar = Scalebar()

layout.addWidget(cps[0], 0, 0, 2, 2)
layout.addWidget(cps[1], 0, 2, 2, 2)
layout.addWidget(cps[2], 0, 4, 2, 1)

layout.addWidget(cps[3], 2, 0, 2, 2)
layout.addWidget(cps[4], 2, 2, 1, 2)
layout.addWidget(cps[5], 3, 2, 1, 3)

ti = pg.TextItem('T E S T', anchor=(0.5, 0.5))
scalebar.addItem(ti)
ti.setPos(0.5, 0.5)
layout.addWidget(scalebar, 3, 3, 1, 3)

ti = pg.TextItem('T E S T')
ch.addItem(ti)
ti.setPos(0.5, 0.5)
layout.addWidget(ch, 4, 0, 2, 5)

for i in range(5) :
    layout.setColumnMinimumWidth(i, 50)
    layout.setColumnStretch(i, 1)
for i in range(4) :
    layout.setRowMinimumHeight(i, 50)
    layout.setRowStretch(i, 1)

# Plot some data
cp0 = cps[0]
x = np.arange(0, 2, 0.1)
y = np.random.rand(len(x))
cp0.plot(x, y)

# Add a second axis
#cp.showAxis('top')
#cp0.plotItem.layout.removeItem(cp0.getAxis('top'))
#topax = pg.AxisItem(orientation='top')
#topax.setRange(-10, 20)
#cp0.plotItem.axes['top']['item'] = topax
#cp0.plotItem.layout.addItem(topax, 1, 1)

ch.pos[1].set_value(0.5)
print(ch.crosshair.hpos.allowed_values)
print(ch.crosshair.hline.maxRange[:])

widget.show()
app.exec_()



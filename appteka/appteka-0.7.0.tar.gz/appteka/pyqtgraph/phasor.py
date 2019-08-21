# appteka - helpers collection

# Copyright (C) 2018-2019 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Implementation of the phasor diagram."""

import math
import pyqtgraph as pg

DEFAULT_CIRCLES_NUM = 6


class PhasorDiagram(pg.PlotWidget):
    """Widget for plotting phasor diagram."""
    def __init__(self, size=500):
        super().__init__()
        self.setAspectLocked(True)
        self.addLine(x=0, pen=0.2)
        self.addLine(y=0, pen=0.2)
        self.showAxis('bottom', False)
        self.showAxis('left', False)

        # fix size
        self.setFixedSize(size, size)

        self.__build_grid()
        self.__build_labels()

        self.set_range(1)

        self.phasors = {}

    def set_range(self, value):
        """Set range of diagram."""
        self.__update_grid(value)
        self.__update_labels(value)

    def __build_grid(self):
        self.circles = []
        for i in range(DEFAULT_CIRCLES_NUM):
            circle = pg.QtGui.QGraphicsEllipseItem()
            circle.setPen(pg.mkPen(0.2))
            self.circles.append(circle)
            self.addItem(circle)

    def __build_labels(self):
        self.labels = []
        for i in range(2):
            label = pg.TextItem()
            self.labels.append(label)
            self.addItem(label)

    def __update_grid(self, value):
        for i in range(DEFAULT_CIRCLES_NUM):
            r = (i + 1) * value / DEFAULT_CIRCLES_NUM
            self.circles[i].setRect(-r, -r, r*2, r*2)

    def __update_labels(self, value):
        self.labels[0].setText("{}".format(value / 2))
        self.labels[0].setPos(value / 2, 0)
        self.labels[1].setText("{}".format(value))
        self.labels[1].setPos(value, 0)

    def add_phasor(self, name, am=0, ph=0, color=(255, 255, 255)):
        """Add phasor to the diagram."""
        phasor = {
            'end': (
                am * math.cos(ph),
                am * math.sin(ph)
            ),
            'line': self.plot(),
        }
        phasor['point'] = self.plot(pen=None, symbolBrush=color,
                                    symbolSize=7, symbolPen=None,
                                    name=name)
        phasor['line'].setPen(color)
        self.phasors[name] = phasor
        self.__update()

    def update_phasor(self, name, am, ph):
        """Change phasor value."""
        self.phasors[name]['end'] = (
            am * math.cos(ph),
            am * math.sin(ph)
        )
        self.__update()

    def __update(self):
        for key in self.phasors:
            phasor = self.phasors[key]
            x = phasor['end'][0]
            y = phasor['end'][1]
            phasor['line'].setData([0, x], [0, y])
            phasor['point'].setData([x], [y])

    def show_legend(self):
        """Show legend."""
        self.plotItem.addLegend()
        for key in self.phasors:
            self.plotItem.legend.addItem(
                self.phasors[key]['line'], key
            )

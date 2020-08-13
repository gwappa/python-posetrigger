#
# MIT License
#
# Copyright (c) 2020 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import numpy as _np
import matplotlib.pyplot as _plt
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as _pg
from . import debug as _debug

COLORMAP = _plt.get_cmap("rainbow")
SPOTSIZE = 20

def colormap(total):
    def color_for_index(i):
        r, g, b, a = COLORMAP((i+1)/(total+1))
        return (int(r*255), int(g*255), int(b*255))
    return color_for_index

def image_to_display(img):
    if img.ndim == 3:
        return img.transpose((1,0,2))
    else:
        return img.T

class FrameView(QtWidgets.QGraphicsView):
    """a thin wrapper class that is used to display acquired frames.
    the `updateWithFrame` method updates what is displayed.
    """
    def __init__(self, width, height, parent=None):
        super().__init__(parent=parent)
        self._width     = width
        self._height    = height
        self._scene     = QtWidgets.QGraphicsScene()
        self._image     = _pg.ImageItem(_np.zeros((width,height), dtype=_np.uint16),
                                        levels=(0, 65535), autolevels=False)
        self._levels    = (0, 65535)
        self._bodyparts = None

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scene.addItem(self._image)
        self.setScene(self._scene)

    def setRange(self, m, M):
        self._levels = (m, M)
        self._image.setLevels(self._levels)

    def updateWithAcquisition(self, mode, acq):
        if mode == "":
            acq.frameAcquired.disconnect(self.updateWithFrame)
        else:
            acq.frameAcquired.connect(self.updateWithFrame)

    def updateWithFrame(self, img, estimation, timestamp):
        self._image.setImage(image_to_display(img), levels=self._levels, autolevels=False)
        if (self._bodyparts is not None) and ("pose" in estimation.keys()):
            pose = estimation["pose"]
            for i, part in enumerate(self._bodyparts):
                part.setPosition(pose[i,:2])
            self._scene.changed.emit([QtCore.QRectF(0, 0, self._width, self._height)])

    def registerBodyParts(self, parts):
        # removing old annotations
        if self._bodyparts is not None:
            for anno in self._bodyparts:
                self._scene.removeItem(anno.spot)
            self._bodyparts = None

        # adding new annotations
        total = len(parts)
        if total == 0:
            return
        self._bodyparts = []
        cmap = colormap(total)
        for i, part in enumerate(parts):
            anno = Annotation(part, dims=(self._width, self._height), color=cmap(i))
            self._scene.addItem(anno.spot)
            self._bodyparts.append(anno)

class Annotation:
    def __init__(self, name, dims, initial=(0, 0),
                 color="y", spotsize=SPOTSIZE):
        self.name   = name
        self._dims  = _np.array(dims)
        self._dia   = spotsize / 2
        self.spot   = QtWidgets.QGraphicsEllipseItem(initial[0]-self._dia,
                                                     initial[1]-self._dia,
                                                     self._dia,
                                                     self._dia)
        self._color = _pg.mkColor(color)
        self.spot.setPen(QtGui.QPen(self._color))
        self.spot.setVisible(False)

    def setPosition(self, xy):
        self.spot.setPos(xy[0]-self._dia, xy[1]-self._dia)
        self.spot.setVisible( all(xy>=0) and all(xy<=self._dims) )

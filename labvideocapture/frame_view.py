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

JET      = _plt.get_cmap("jet")
SPOTSIZE = 20

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
        self._image     = _pg.ImageItem(_np.zeros((width,height), dtype=_np.uint16))
        self._bodyparts = None

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scene.addItem(self._image)
        self.setScene(self._scene)

    def updateWithAcquisition(self, mode, acq):
        if mode == "":
            acq.frameAcquired.disconnect(self.updateWithFrame)
        else:
            acq.frameAcquired.connect(self.updateWithFrame)

    def updateWithFrame(self, img, timestamp):
        self._image.setImage(image_to_display(img))

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
        for i, part in enumerate(parts):
            d    = (i+1)*40 # just for the temporary debug purpose
            anno = Annotation(part, initial=((d,),(d,)))
            self._scene.addItem(anno.spot)
            self._bodyparts.append(anno)

    def annotatePositions(self, pose, timestamp):
        if self._bodyparts is not None:
            for i, part in enumerate(self._bodyparts):
                part.setPosition(pose[i,:2])

class Annotation:
    def __init__(self, name, initial=((0,),(0,)),
                 color="y", spotsize=SPOTSIZE):
        self.name   = name
        self.spot   = _pg.ScatterPlotItem(pos=initial, size=spotsize, pen=_pg.mkPen(color))
    
    def setPosition(self, xy):
        self.spot.setData(pos=xy.reshape((2,1)))
        
        

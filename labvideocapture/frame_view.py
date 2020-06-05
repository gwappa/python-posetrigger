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
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import pyqtgraph as _pg
from . import debug as _debug

def image_to_display(img):
    if img.ndim == 3:
        return img.transpose((1,0,2))
    else:
        return img.T

class FrameView(QtWidgets.QGraphicsView):
    """a thin wrapper class that is used to display acquired frames.
    the `update_with_image` method updates what is displayed.
    """
    def __init__(self, width, height, parent=None):
        super().__init__(parent=parent)
        self._width  = width
        self._height = height
        self._scene  = QtWidgets.QGraphicsScene()
        self._image  = _pg.ImageItem(_np.zeros((width,height), dtype=_np.uint16))

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scene.addItem(self._image)
        self.setScene(self._scene)

    def update_with_acquisition_mode(self, mode, acq):
        if mode == "":
            acq.frameAcquired.disconnect(self.update_with_image)
        else:
            acq.frameAcquired.connect(self.update_with_image)

    def update_with_image(self, img):
        self._image.setImage(image_to_display(img))

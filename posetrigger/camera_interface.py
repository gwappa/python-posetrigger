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

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import timedcapture as _cap
from . import debug as _debug

def load_device(path):
    return _cap.Device(path)

class CameraInterface(QtGui.QGroupBox):
    """the UI for the control of exposure/gain of the device to be used.
    it has path/width/height properties to refer to (but fixed)."""
    def __init__(self, device, parent=None):
        super().__init__(f"Camera '{device.path}'", parent=parent)
        self._device   = device
        self._has_strobe = True

        self._exposure = QtGui.QSpinBox()
        self._exposure.setMinimum(1)
        self._exposure.setMaximum(1000000)
        self._exposure.setValue(self._device.exposure_us)
        self._exposure.valueChanged.connect(self.update_exposure)

        self._gain     = QtGui.QSpinBox()
        self._gain.setMinimum(0)
        self._gain.setMaximum(480)
        self._gain.setValue(self._device.gain)
        self._gain.valueChanged.connect(self.update_gain)

        self._layout = QtGui.QFormLayout()
        self._layout.addRow("exposure (us)", self._exposure)
        self._layout.addRow("gain", self._gain)
        self.setLayout(self._layout)

    def updateWithAcquisition(self, mode, acq):
        if mode == "ACQUIRE":
            if self._has_strobe == True:
                try:
                    self._device.strobe = True
                except RuntimeError:
                    _debug("failed to turn on the strobe output (probably not a supported device)")
                    self._has_strobe = False
            for attr in ("width", "height", "exposure_us", "gain"):
                acq.setStaticMetadata(attr, getattr(self._device, attr))
        else:
            if self._has_strobe == True:
                try:
                    self._device.strobe = False
                except RuntimeError:
                    _debug("failed to control the strobe output (probably not a supported device)")
                    self._has_strobe = False

    @property
    def path(self):
        return self._device.path

    @property
    def width(self):
        return self._device.width

    @property
    def height(self):
        return self._device.height

    def update_exposure(self, value):
        self._device.exposure_us = int(value)

    def update_gain(self, value):
        self._device.gain = int(value)

    def teardown(self):
        self._device.close()

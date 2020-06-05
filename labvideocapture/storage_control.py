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
from time import time as _now
import datetime as _datetime
import numpy as _np
import bzar as _bzar
from . import debug as _debug
from . import acquisition_control as _actrl

DEFAULT_FORMAT = "out_%Y-%m-%d_run%H%M%S"

class StorageControl(QtGui.QGroupBox):
    statusUpdated = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__("Storage", parent=parent)
        self._format = QtGui.QLineEdit(DEFAULT_FORMAT)
        self._suffix = QtGui.QLabel(".npz")
        self._layout = QtGui.QFormLayout()
        self._layout.addRow("File-name format", self._format)
        self._layout.addRow("Suffix", self._suffix)
        self.setLayout(self._layout)
        self._path    = None
        self._out     = None
        self._stamps  = None
        self._nframes = 0

    def update_with_acquisition_mode(self, mode, acquisition):
        if mode == _actrl.LABEL_FOCUS:
            pass
        elif mode == _actrl.LABEL_ACQUIRE:
            self._path = _datetime.datetime.now().strftime(self._format.text()) + self._suffix.text()
            _debug(f"opening storage: {self._path}")
            self._stamps  = []
            self._out     = []
            self._nframes = 0
            acquisition.frameAcquired.connect(self.add_frame)
        else:
            self.close()

    def add_frame(self, frame, timestamp):
        self._stamps.append(timestamp)
        self._out.append(_np.array(frame, copy=True))
        self._nframes += 1
        if self._nframes % 100 == 0:
            self.statusUpdated.emit(f"collected >{self._nframes} frames...")

    def close(self):
        if self._out is not None:
            _debug(f"closing storage: {self._path}")
            with open(self._path, "wb") as out:
                _np.savez(out, frames=_np.stack(self._out, axis=0), timestamps=_np.array(self._stamps))
            self._out  = None
            self._path = None

    def teardown(self):
        self.close()

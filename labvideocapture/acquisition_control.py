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
import numpy as _np
from . import debug as _debug

class AcquisitionControl(QtGui.QGroupBox):
    statusUpdated  = QtCore.pyqtSignal(str)
    frameAcquired  = QtCore.pyqtSignal(_np.ndarray)
    starting       = QtCore.pyqtSignal()
    stopping       = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Acquisition", parent=None)
        self._mode     = "" # holds the current mode
        self._storage  = None
        self._acq      = None

        self._basename = QtGui.QLineEdit("out")
        self._focus    = RunButton("FOCUS")
        self._focus.startRequested.connect(self.start_focus)
        self._focus.stopRequested.connect(self.stop_focus)
        self._acquire  = RunButton("ACQUIRE")
        self._acquire.startRequested.connect(self.start_acquisition)
        self._acquire.stopRequested.connect(self.stop_acquisition)
        self.statusUpdated.connect(self._focus.set_status)
        self.statusUpdated.connect(self._acquire.set_status)

        self._label    = QtGui.QLabel("")

        self._layout = QtGui.QFormLayout()
        self._layout.addRow("Base name", self._basename)
        self.setLayout(self._layout)

    @property
    def focusbutton(self):
        return self._focus

    @property
    def acquirebutton(self):
        return self._acquire

    @property
    def statuslabel(self):
        return self._label

    def update_with_model(self, running):
        if running == True:
            pass
        else:
            if self._mode == "ACQUIRE":
                pass
            self._mode = ""
        self._label.setText("")
        self.statusUpdated.emit(self._mode)

    def start_focus(self):
        self._mode = "FOCUS"
        self.starting.emit()

    def stop_focus(self):
        self._mode = "FOCUS"
        self._focus.setEnabled(False)
        self._label.setText("terminating the FOCUS mode...")
        QtCore.QCoreApplication.processEvents()
        self.stopping.emit()

    def start_acquisition(self):
        self._mode = "ACQUIRE"
        self._storage = DefaultVideoWriter(self._filepath.text())
        self._model.frameAcquired.connect(self._storage.write, type=QtCore.Qt.QueuedConnection)
        self.starting.emit()

    def stop_acquisition(self):
        self._mode = "ACQUIRE"
        self._acquire.setEnabled(False)
        self._label.setText("terminating the ACQUIRE mode...")
        QtCore.QCoreApplication.processEvents()
        self.stopping.emit()

class RunButton(QtGui.QPushButton):
    """the UI part for FOCUS/ACQUIRE buttons.
    The startRequested() and the stopRequested() signals
    correspond to requesting of start/stop acquisition.
    """
    startRequested = QtCore.pyqtSignal(str)
    stopRequested  = QtCore.pyqtSignal(str)

    def __init__(self, title, alt_title="STOP", parent=None):
        super().__init__(title, parent=parent)
        self._basetext = title
        self._alttext  = alt_title
        self.setCheckable(True)
        self.clicked.connect(self.emit_request)

    def emit_request(self, checked):
        if self.text() == self._basetext:
            _debug(f"starting: {self._basetext}")
            self.startRequested.emit(self._basetext)
        else:
            _debug(f"stopping: {self._basetext}")
            self.stopRequested.emit(str)
        # wait for the other processes to update the status
        self.setChecked(not checked)

    def set_status(self, status):
        if status == self._basetext:
            _debug(f"{self._basetext} started")
            self.setEnabled(True)
            self.setText(self._alttext)
            self.setChecked(True)
        elif len(status) == 0:
            _debug(f"{self._basetext}: reverting to base status")
            self.setEnabled(True)
            self.setText(self._basetext)
            self.setChecked(False)
        else:
            _debug(f"disabling {self._basetext}")
            self.setEnabled(False)

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
from . import acquisition as _acquisition

LABEL_FOCUS      = "FOCUS"
LABEL_ACQUIRE    = "ACQUIRE"
DEFAULT_INTERVAL = 10

TIMING           = _acquisition.BusyWait

class AcquisitionControl(QtGui.QGroupBox):
    modeIsChanging = QtCore.pyqtSignal(str, object)
    statusUpdated  = QtCore.pyqtSignal(str)
    frameAcquired  = QtCore.pyqtSignal(_np.ndarray)

    def __init__(self, device, parent=None):
        super().__init__("Acquisition", parent=None)
        self._mode     = "" # holds the current mode
        self._device   = device
        self._acq      = None
        self._timing   = None

        self._interval = QtGui.QSpinBox()
        self._interval.setMinimum(5)
        self._interval.setMaximum(10000)
        self._interval.setValue(DEFAULT_INTERVAL)
        self._focus    = RunButton(LABEL_FOCUS)
        self._focus.startRequested.connect(self.process_start)
        self._focus.stopRequested.connect(self.process_stop)
        self._acquire  = RunButton(LABEL_ACQUIRE)
        self._acquire.startRequested.connect(self.process_start)
        self._acquire.stopRequested.connect(self.process_stop)
        self.statusUpdated.connect(self._focus.set_status)
        self.statusUpdated.connect(self._acquire.set_status)

        self._label    = QtGui.QLabel("")

        self._layout = QtGui.QFormLayout()
        self._layout.addRow("Acquisition interval (ms)", self._interval)
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

    def show_storage_status(self, msg):
        self._label.setText(msg)

    def flag_acquisition_started(self):
        self._label.setText("")
        self.statusUpdated.emit(self._mode)

    def revert_to_idle(self):
        self._mode = ""
        self._label.setText("")
        self._acq.wait();
        self.modeIsChanging.emit(self._mode, self._acq)
        self._acq = None
        self._timing.quit()
        self._timing.wait()
        self._timing = None
        self.statusUpdated.emit(self._mode)

    def process_start(self, mode):
        if mode == LABEL_FOCUS:
            pass
        elif mode == LABEL_ACQUIRE:
            pass
        else:
            raise ValueError(f"unknown mode: {mode}")
        self._mode   = mode
        self._acq    = _acquisition.Acquisition(self._device)
        self.modeIsChanging.emit(self._mode, self._acq)
        self._timing = TIMING(self._interval.value(), self._acq)
        self._acq.acquisitionStarting.connect(self.flag_acquisition_started)
        self._acq.acquisitionEnding.connect(self.revert_to_idle)
        self._acq.start()

    def process_stop(self, mode):
        if (self._mode != mode):
            raise RuntimeError(f"mode mismatch: {self._mode} on AcquisitionControl, got {mode}")
        if mode == LABEL_FOCUS:
            pass
        elif mode == LABEL_ACQUIRE:
            pass
        else:
            raise ValueError(f"unknown mode: {mode}")
        self._label.setText(f"terminating the {mode} mode...")
        self._acq.request_quit()

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
            # _debug(f"starting: {self._basetext}")
            self.startRequested.emit(self._basetext)
        else:
            # _debug(f"stopping: {self._basetext}")
            self.stopRequested.emit(self._basetext)
        # wait for the other processes to update the status
        self.setChecked(not checked)

    def set_status(self, status):
        if status == self._basetext:
            # _debug(f"{self._basetext} started")
            self.setEnabled(True)
            self.setText(self._alttext)
            self.setChecked(True)
        elif len(status) == 0:
            # _debug(f"{self._basetext}: reverting to base status")
            self.setEnabled(True)
            self.setText(self._basetext)
            self.setChecked(False)
        else:
            # _debug(f"disabling {self._basetext}")
            self.setEnabled(False)

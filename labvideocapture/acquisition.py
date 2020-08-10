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
from time import time as _now
from . import debug as _debug

DEFAULT_PRIORITY = QtCore.QThread.TimeCriticalPriority

class _AcquisitionInterrupt:
    """a context-manager object to interact with an Acquisition object.
    it automatically locks and unlocks the acquisition mutex."""
    def __init__(self, parent):
        self._parent = acq

    def __enter__(self):
        self._parent._acquisition.lock()
        return self

    def wait_for_capture(self):
        self._parent._captured.wait(self._parent._acquisition)

    def trigger_capture(self):
        self._triggered.wakeAll()

    def __exit__(self, *args):
        self._parent._acquisition.unlock()

class IntervalGeneration(QtCore.QThread):
    """the thread that governs timing generation based on QTimer."""
    def __init__(self, interval_ms, acquisition, parent=None):
        super().__init__(parent=parent)
        self._timer = QtCore.QTimer()
        self._timer.moveToThread(self)
        self._timer.setTimerType(QtCore.Qt.PreciseTimer)
        self._timer.setSingleShot(False)
        self._timer.setInterval(interval_ms)

        acquisition.acquisitionStarting.connect(self.start)
        self.started.connect(self._timer.start)
        self.started.connect(self.raise_priority)
        self._timer.timeout.connect(acquisition.trigger_capture)
        acquisition.acquisitionEnding.connect(self.quit)
        acquisition.acquisitionEnding.connect(self._timer.stop)

    def raise_priority(self):
        self.setPriority(QtCore.QThread.TimeCriticalPriority)

class Acquisition(QtCore.QThread):
    """the class that governs acquisition from the camera."""
    acquisitionStarting = QtCore.pyqtSignal()
    frameAcquired       = QtCore.pyqtSignal(_np.ndarray, float)
    acquisitionEnding   = QtCore.pyqtSignal()

    def __init__(self, device, priority=None, parent=None):
        """device: timedcapture.Device"""
        super().__init__(parent=parent)
        self._device      = device
        self._acquisition = QtCore.QMutex()
        self._triggered   = QtCore.QWaitCondition() # used with _acquisition
        self._captured    = QtCore.QWaitCondition() # used with _acquisition
        self._toquit      = False # used with _acquisition
        self._priority    = DEFAULT_PRIORITY if priority is None else priority
        self.started.connect(self.raise_priority)

    @property
    def width(self):
        return self._device.width

    @property
    def height(self):
        return self._device.height

    def raise_priority(self):
        self.setPriority(self._priority)

    def hold(self):
        """returns a context manager to lock the acqusition mutex."""
        return _AcquisitionInterrupt(self)

    def wait_for_capture(self):
        """waits until a single frame is grabbed."""
        self._acquisition.lock()
        self._captured.wait(self._acquisition)
        self._acquisition.unlock()

    def trigger_capture(self):
        self._acquisition.lock()
        self._triggered.wakeAll()
        self._acquisition.unlock()

    def request_quit(self):
        self._acquisition.lock()
        self._toquit = True
        self._triggered.wakeAll() # just in case it is needed
        self._acquisition.unlock()

    def run(self):
        self._acquisition.lock()
        self._toquit = False
        self._device.start_capture()
        self.acquisitionStarting.emit()
        try:
            while True:
                self._triggered.wait(self._acquisition)
                if self._toquit == True:
                    self.acquisitionEnding.emit()
                    self._captured.wakeAll()
                    return
                self._acquisition.unlock()
                frame = self._device.read_frame()
                self.frameAcquired.emit(frame, _now())
                self._acquisition.lock()
                self._captured.wakeAll()
        finally:
            self._device.stop_capture()
            self._acquisition.unlock()

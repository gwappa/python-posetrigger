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
DEFAULT_SUFFIX = ".npz"

class Storage(QtCore.QObject):
    statusUpdated = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._format  = DEFAULT_FORMAT
        self._suffix  = DEFAULT_SUFFIX

        self._path    = None
        self._out     = None
        self._frametime  = None
        self._nframes = 0
        self._bodyparts = None
        self._posetime  = None
        self._pose      = None

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, fmt):
        self._format = fmt

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self, suffix):
        self._suffix = suffix

    def updateWithAcquisition(self, mode, acquisition):
        if mode == _actrl.LABEL_FOCUS:
            pass
        elif mode == _actrl.LABEL_ACQUIRE:
            self._path = _datetime.datetime.now().strftime(self._format) + self._suffix
            _debug(f"opening storage: {self._path}")
            self._frametime  = []
            if self._bodyparts is not None:
                self._posetime = []
                self._pose     = []
            self._out     = []
            self._nframes = 0
            acquisition.frameAcquired.connect(self.addFrame)
        else:
            self.close()

    def updateWithBodyParts(self, parts):
        if len(parts) > 0:
            self._bodyparts = parts
        else:
            self._bodyparts = None

    def addFrame(self, frame, timestamp):
        self._frametime.append(timestamp)
        self._out.append(_np.array(frame, copy=True))
        self._nframes += 1
        if self._nframes % 100 == 0:
            self.statusUpdated.emit(f"collected >{self._nframes} frames...")

    def addPose(self, pose, timestamp):
        if self._pose is not None:
            self._pose.append(pose)
            self._posetime.append(timestamp)

    def close(self):
        if self._out is not None:
            _debug(f"closing storage: {self._path}")
            values = dict(frames=_np.stack(self._out, axis=0), timestamps=_np.array(self._frametime))
            if self._pose is not None:
                values["bodyparts"] = self._bodyparts
                values["pose"]      = _np.stack(self._pose, axis=0)
                values["pose_timestamps"] = _np.array(self._posetime)
            with open(self._path, "wb") as out:
                _np.savez(out, **values)
            self._out       = None
            self._path      = None
            self._posetime  = None
            self._pose      = None

    def teardown(self):
        self.close()

class StorageControl(QtGui.QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Storage", parent=parent)
        self._model  = Storage()
        self.statusUpdated         = self._model.statusUpdated
        self.updateWithAcquisition = self._model.updateWithAcquisition
        self.updateWithBodyParts   = self._model.updateWithBodyParts
        self.addPose               = self._model.addPose

        self._format = QtGui.QLineEdit(self._model.format)
        self._suffix = QtGui.QLabel(self._model.suffix)
        self._format.editingFinished.connect(self._updateFormat)

        self._layout = QtGui.QFormLayout()
        self._layout.addRow("File-name format", self._format)
        self._layout.addRow("Suffix", self._suffix)
        self.setLayout(self._layout)

    @property
    def model(self):
        return self._model

    def _updateFormat(self):
        self._model.format = self._format.text()

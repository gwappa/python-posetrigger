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

from pathlib import Path
import numpy as _np
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from cv2 import resize as _resize, \
                INTER_NEAREST as _INTER_NEAREST
import dlclib as _dlclib # TODO: make it optional
from . import debug as _debug
from .expression import parse as _parse_expression, \
                        ParseError as _ParseError

LOCATE_ON_GPU = True
FRAME_WIDTH   = 640
FRAME_HEIGHT  = 480
RESIZE_WIDTH  = 320

def return_false(pose):
    return False

class Evaluation(QtCore.QObject):
    errorOccurredOnLoading = QtCore.pyqtSignal(str, str)
    evaluationModeLocked   = QtCore.pyqtSignal(bool)
    bodypartsUpdated       = QtCore.pyqtSignal(tuple)
    estimationUpdated      = QtCore.pyqtSignal(_np.ndarray, float)
    currentlyWorkingOn     = QtCore.pyqtSignal(str)
    statusUpdated          = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._evaluated  = False
        self._cfgpath    = None
        self._parts      = []
        self._session    = None
        self._expression = None
        self._origshape  = None
        self._buffer     = None
        self._resizedims = None
        self._scale      = 1

    def updateWithProject(self, path: str):
        if path == "":
            self._parts = []
            self.bodypartsUpdated.emit(tuple())
            self._session = None
            return

        # has value in path
        _debug(f"load DLC project: {path}")
        self._cfgpath = Path(path) / "config.yaml"

        # try to load body parts
        try:
            cfgdata     = _dlclib.load_config(self._cfgpath)
            self._parts = tuple(cfgdata["bodyparts"])
            self.bodypartsUpdated.emit(self._parts)
        except Exception as e:
            self.errorOccurred.emit("failed to open the DLC project", f"{e}")
            return

        # try to load session
        self._session = _dlclib.estimate.TFSession.from_config(self._cfgpath,
                                                               locate_on_gpu=LOCATE_ON_GPU)

    def setEvaluationEnabled(self, val: bool):
        _debug(f"evaluation --> {val}")
        self._evaluated = val

    def setExpression(self, expr):
        if expr is None:
            _debug(f"cleared expression")
            self._expression = return_false
        else:
            _debug(f"expression --> {expr}")
            self._expression = expr

    def updateWithAcquisition(self, mode, acq):
        if mode != "":
            # starting acquisition
            if self._session is not None:
                acq.setEvaluator(self.estimateFromFrame)
                self._prepareBuffer(acq.width, acq.height)
            self.evaluationModeLocked.emit(True)
        else:
            # stopping acquisition
            if self._session is not None:
                self._clearBuffer()
            self.evaluationModeLocked.emit(False)

    def _prepareBuffer(self, width, height):
        self._origshape = (height, width, 1)
        self._buffer    = _np.empty((height, width, 3), dtype=_np.uint8)
        if RESIZE_WIDTH == width:
            self._resizedims = (width, height)
            self._scale      = 1
        else:
            self._scale      = width / RESIZE_WIDTH
            self._resizedims = (RESIZE_WIDTH, int(height / self._scale))
        self._session.get_pose(_resize(self._buffer,
                                       self._resizedims,
                                       interpolation=_INTER_NEAREST))

    def _clearBuffer(self):
        self._buffer     = None
        self._resizedims = None
        self._scale      = 1

    def estimateFromFrame(self, frame):
        if self._session is not None:
            self._buffer[:] = (frame / 256).reshape(self._origshape)
            pose            = self._session.get_pose(_resize(self._buffer,
                                                             self._resizedims,
                                                             interpolation=_INTER_NEAREST))
            pose[:,:2] = pose[:,:2] * self._scale
            status = self._expression(pose) if self._evaluated == True else None
            return pose, status
        else:
            return None, None

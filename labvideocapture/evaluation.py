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
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import dlclib as _dlclib # TODO: make it optional
from . import debug as _debug
from .expression import parse as _parse_expression, \
                        ParseError as _ParseError

class Evaluation(QtCore.QObject):
    errorOccurredOnLoading = QtCore.pyqtSignal(str, str)
    bodypartsUpdated       = QtCore.pyqtSignal(tuple)
    currentlyWorkingOn     = QtCore.pyqtSignal(str)
    statusUpdated          = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._evaluated = False
        self._parts     = []
        self._evaluator = None

    def updateWithProject(self, path: str):
        if path is None:
            _debug("TODO: clear current DLC project")
            # TODO
            return

        # has value in path
        _debug(f"load DLC project: {path}")
        path    = Path(path)
        try:
            cfgdata     = _dlclib.load_config(path / "config.yaml")
            self._parts = tuple(cfgdata["bodyparts"])
            self.bodypartsUpdated.emit(self._parts)
        except Exception as e:
            self.errorOccurred.emit("failed to open the DLC project", f"{e}")
            return
        # TODO: load session

    def setEvaluationEnabled(self, val: bool):
        _debug(f"evaluation --> {val}")
        self._evaluated = val

    def setExpression(self, expr):
        if expr is None:
            _debug(f"cleared expression")
            self._evaluator = None
        else:
            _debug(f"expression --> {expr}")
            self._evaluator = expr

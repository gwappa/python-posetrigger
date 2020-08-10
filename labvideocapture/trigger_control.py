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
from . import debug as _debug

class TriggerOutput(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._triggered = False
        self._acq       = None

    @property
    def enabled(self):
        return self._triggered

    @enabled.setter
    def enabled(self, val: bool):
        self._triggered = val
        if self._acq is not None:
            self._acq.setTriggerOutput(self.updateOutput if val == True else None)

    def updateWithAcquisition(self, mode, acq):
        if mode != "":
            # starting
            self._acq = acq
            acq.setTriggerOutput(self.updateOutput if self._triggered == True else None)
        else:
            # ending
            self._acq = None

    def updateOutput(self, val: bool):
        _debug(f"trigger --> {val}")

class TriggerControl(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Trigger generation", parent=parent)
        self._model  = TriggerOutput()
        self.updateWithAcquisition = self._model.updateWithAcquisition

        self._enable = QtWidgets.QCheckBox("Enable trigger output")
        self._header = QtWidgets.QLabel("Trigger UDP port: ")
        self._field  = PortEditor("6666")
        self._tester = QtWidgets.QPushButton("Toggle Manually")
        self._tester.setCheckable(True)
        self._tester.setChecked(False)
        self._enable.stateChanged.connect(self.updateInterface)

        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._enable, 0, 0, 1, 3)
        self._layout.addWidget(self._header, 1, 0)
        self._layout.addWidget(self._field, 1, 1)
        self._layout.addWidget(self._tester, 1, 2)
        self.setLayout(self._layout)

        self.setTriggerable(False)

    def setTriggerable(self, val: bool):
        self._enable.setEnabled(val)
        self.updateInterface()

    def updateInterface(self, notused=None):
        status = self._enable.isEnabled() and (self._enable.checkState() != QtCore.Qt.Unchecked)
        self._tester.setEnabled(not status)
        self._model.enabled = status

class PortEditor(QtWidgets.QLineEdit):
    def __init__(self, content, parent=None):
        super().__init__(content, parent=parent)

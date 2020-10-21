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
from . import trigger as _trigger

def _do_nothing(*args, **kwargs):
    pass

class TriggerControl(QtWidgets.QGroupBox):

    def __init__(self, parent=None):
        super().__init__("Trigger generation", parent=parent)
        try:
            self._model  = _trigger.TriggerOutput()
            self.updateWithAcquisition = self._model.updateWithAcquisition
            self.teardown              = self._model.teardown
        except ConnectionError:
            QtWidgets.QMessageBox.warning(self, "Failed to connect to FastEventServer",
                """LabVideoCapture failed to establish a connection to FastEventServer.
The trigger-generation functionality will be disabled.

To enable it, launch FastEventServer first, and re-launch LabVideoCapture.""")
            self._model  = None
            self.updateWithAcquisition = _do_nothing
            self.teardown              = _do_nothing

        self._enable = QtWidgets.QCheckBox("Enable trigger output")
        self._header = QtWidgets.QLabel("Trigger UDP port: ")
        self._field  = PortEditor("11666") # TODO: reflect to _model
        self._tester = QtWidgets.QPushButton("Toggle Manually")
        self._tester.setCheckable(True)
        self._tester.setChecked(False)
        self._tester.clicked.connect(self.updateWithToggle)
        self._enable.stateChanged.connect(self.updateInterface)

        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._enable, 0, 0, 1, 3)
        self._layout.addWidget(self._header, 1, 0)
        self._layout.addWidget(self._field, 1, 1)
        self._layout.addWidget(self._tester, 1, 2)
        self.setLayout(self._layout)

        self.setTriggerable(False)
        if self._model is None:
            self._disableAllControls()

    def _disableAllControls(self):
        for elem in (self._enable, self._header, self._field, self._tester):
            elem.setEnabled(False)
        self.setTitle("Trigger generation (disabled)")

    def setTriggerable(self, val: bool):
        if self._model is not None:
            self._enable.setEnabled(val)
            self.updateInterface()

    def updateInterface(self, notused=None):
        if self._model is not None:
            status = self._enable.isEnabled() and (self._enable.checkState() != QtCore.Qt.Unchecked)
            self._tester.setEnabled(not status)
            self._model.enabled = status

    def updateWithToggle(self):
        if self._model is not None:
            self._model.updateOutput(self._tester.isChecked())

class PortEditor(QtWidgets.QLineEdit):
    def __init__(self, content, parent=None):
        super().__init__(content, parent=parent)

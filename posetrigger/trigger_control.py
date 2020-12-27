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
from . import service as _service

def _do_nothing(*args, **kwargs):
    pass

def _mock_updateWithAcquisition(mode, acq):
    if mode != "":
        acq.setStaticMetadata("trigger", None)

class ServiceControl(QtWidgets.QWidget):
    LAUNCH   = "Launch FastEventServer"
    SHUTDOWN = "Shutdown FastEventServer"

    launched          = QtCore.pyqtSignal(int)
    shutdownRequested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._driverheader = QtWidgets.QLabel("Driver type: ")
        self._driverfield  = DriverSelector()
        self._serialheader = QtWidgets.QLabel("Serial device: ")
        self._serialfield  = SerialEditor()
        self._udpheader    = QtWidgets.QLabel("Use UDP port: ")
        self._udpfield     = PortEditor() # TODO: reflect to _model
        self._toggle       = QtWidgets.QPushButton(self.LAUNCH)
        self._toggle.clicked.connect(self.toggle)

        self._layout     = QtGui.QGridLayout()
        self._layout.addWidget(self._driverheader, 0, 0)
        self._layout.addWidget(self._driverfield, 0, 1)
        self._layout.addWidget(self._serialheader, 1, 0)
        self._layout.addWidget(self._serialfield, 1, 1)
        self._layout.addWidget(self._udpheader, 2, 0)
        self._layout.addWidget(self._udpfield, 2, 1)
        self._layout.addWidget(self._toggle, 3, 1, 1, 2)
        self.setLayout(self._layout)

    def toggle(self):
        current = self._toggle.text()
        if current == self.LAUNCH:
            self.launch()
        else:
            self.shutdownRequested.emit()

    def launch(self):
        _service.launch()
        self.launched.emit(self._udpfield.value)
        self._toggle.setText(self.SHUTDOWN)
        self.setEditable(False)

    def shutdown(self):
        _service.shutdown()
        self._toggle.setText(self.LAUNCH)
        self.setEditable(True)

    def setEditable(self, value):
        for item in (self._driverheader,
                     self._driverfield,
                     self._serialheader,
                     self._serialfield,
                     self._udpheader,
                     self._udpfield):
            item.setEnabled(value)

class TriggerControl(QtWidgets.QGroupBox):
    serviceCanShutdown = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__("Trigger generation", parent=parent)

        self._enable = QtWidgets.QCheckBox("Enable trigger output")
        self._tester = QtWidgets.QPushButton("Toggle Manually")
        self._tester.setCheckable(True)
        self._tester.setChecked(False)
        self._tester.clicked.connect(self.updateWithToggle)
        self._enable.stateChanged.connect(self.updateInterface)

        self.resetConnection()
        self._service = ServiceControl()
        self._service.launched.connect(self.openConnection)
        self._service.shutdownRequested.connect(self.closeConnection)
        self.serviceCanShutdown.connect(self._service.shutdown)
        self.serviceCanShutdown.connect(self.resetConnection)

        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._service, 0, 0, 1, 3)
        self._layout.addWidget(self._enable, 1, 0, 1, 2)
        self._layout.addWidget(self._tester, 1, 2)
        self.setLayout(self._layout)

    def resetConnection(self):
        self._model  = None
        self.setTriggerable(False)
        self.setControlsEnabled(False)

    def closeConnection(self):
        if self._model is not None:
            print("closing the connection to FastEventServer...")
            self._model.teardown()
        self.serviceCanShutdown.emit()

    def openConnection(self, port):
        try:
            print("opening connection to FastEventServer...")
            self._model  = _trigger.TriggerOutput(port)
            self.setControlsEnabled(True)
        except ConnectionError as e:
            from traceback import print_exc
            print_exc()
            self.serviceCanShutdown.emit()

    def setControlsEnabled(self, value):
        for elem in (self._enable, self._tester):
            elem.setEnabled(value)

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

    def updateWithAcquisition(self, mode, acq):
        if self._model is not None:
            self._model.updateWithAcquisition(mode, acq)

    def teardown(self):
        self.disconnect()

class DriverSelector(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        for item in ("uno", "leonardo", "dummy", "dummy-verbose"):
            self.addItem(item)
        self.setEditable(False)
        self.setCurrentText(_service.get_driver_type())

class PortEditor(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(str(self.value), parent=parent)

    @property
    def value(self):
        return _service.get_udp_port()

class SerialEditor(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super().__init__(self.value, parent=parent)

    @property
    def value(self):
        return _service.get_serial_port()

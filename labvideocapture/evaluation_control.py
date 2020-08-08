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

class NotDLCProjectError(ValueError):
    def __init__(self, msg):
        super().__init__(msg)

class Evaluation(QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._evaluated = False
        self._triggered = False

    def updateWithProject(self, path: str):
        if path is not None:
            _debug(f"load DLC project: {path}")

    def setEvaluationEnabled(self, val: bool):
        _debug(f"evaluation --> {val}")
        self._evaluated = val

    def setExpression(self, expr):
        _debug(f"expression --> {expr}")

    def setTriggerEnabled(self, val: bool):
        _debug(f"trigger --> {val}")
        self._triggered = val


class EvaluationControl(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Evaluation", parent=parent)
        self._model    = Evaluation()
        self._loader   = ProjectSelector("DLC Project: ")
        self._expr     = EvaluationEditor()
        self._feedback = FeedbackConfiguration()
        self._loader.projectChanged.connect(self._expr.updateWithProject)
        self._loader.projectChanged.connect(self._model.updateWithProject)
        self._expr.evaluationEnabled.connect(self._feedback.setTriggerable)
        self._expr.evaluationEnabled.connect(self._model.setEvaluationEnabled)
        self._expr.expressionChanged.connect(self._model.setExpression)
        self._feedback.triggerEnabled.connect(self._model.setTriggerEnabled)
        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._loader.header, 1, 0)
        self._layout.addWidget(self._loader.field,  1, 1)
        self._layout.addWidget(self._loader.loadbutton, 1, 2)
        self._layout.addWidget(self._expr.enablebutton, 2, 0, 1, 3)
        self._layout.addWidget(self._expr.header, 3, 0)
        self._layout.addWidget(self._expr.editor, 3, 1, 1, 2)
        self._layout.addWidget(self._feedback.enablebutton, 4, 0, 1, 3)
        self._layout.addWidget(self._feedback.header, 5, 0)
        self._layout.addWidget(self._feedback.port, 5, 1)
        self._layout.addWidget(self._feedback.test, 5, 2)
        self.setLayout(self._layout)

class ProjectSelector(QtCore.QObject):
    """the object for selecting DLC project."""
    projectChanged    = QtCore.pyqtSignal(str)

    NOT_SELECTED   = "<not selected>"

    def __init__(self, labeltext: str, parent=None):
        super().__init__(parent=parent)
        self._header = QtWidgets.QLabel(labeltext)
        self._field  = QtWidgets.QLabel(self.NOT_SELECTED)
        self._load   = QtWidgets.QPushButton("Select...")
        self._path   = None

        self._load.clicked.connect(self.selectProjectByDialog)
        self.updateUI()

    @property
    def header(self):
        return self._header

    @property
    def field(self):
        return self._field

    @property
    def loadbutton(self):
        return self._load

    def updateUI(self):
        if self._path is not None:
            self._field.setText(self._path.name)
            self.setSelectionStatus(True)
        else:
            self._field.setText(self.NOT_SELECTED)
            self.setSelectionStatus(False)

    def setSelectionStatus(self, val: bool):
        for widget in (self._field, ):
            widget.setEnabled(val)

    def setProject(self, path: str):
        path = Path(path)
        # validate
        if not (path / "config.yaml").exists():
            raise NotDLCProjectError(f"'{path.name}' does not seem to be a DLC project")
        self._path = path
        self.updateUI()
        self.projectChanged.emit(str(path))

    def selectProjectByDialog(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self._field,
                                        "Select a DeepLabCut project...",
                                        "",
                                        QtWidgets.QFileDialog.ShowDirsOnly)
        if path == "":
            return
        try:
            self.setProject(path)
        except NotDLCProjectError as e:
            QtWidgets.QMessageBox.warning(self._field, "Failed to select the directory", f"{e}")

class EvaluationEditor(QtCore.QObject):
    evaluationEnabled = QtCore.pyqtSignal(bool)
    expressionChanged = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._enable = QtWidgets.QCheckBox("Enable evaluation")
        self._enable.setCheckState(QtCore.Qt.Unchecked)
        self._header = QtWidgets.QLabel("Expression: ")
        self._field  = QtWidgets.QLineEdit()
        self._enable.stateChanged.connect(self.updateUI)
        self.setEnabled(False)

    @property
    def enablebutton(self):
        return self._enable

    @property
    def header(self):
        return self._header

    @property
    def editor(self):
        return self._field

    def updateWithProject(self, path=None):
        self.setEnabled(path is not None)

    def setEnabled(self, val: bool):
        self._enable.setEnabled(val)
        self.updateUI()

    def updateUI(self, value=None):
        """value: not used"""
        status = self._enable.isEnabled() and (self._enable.checkState() == QtCore.Qt.Checked)
        for widget in (self._header, self._field):
            widget.setEnabled(status)
        self.evaluationEnabled.emit(status)

class PortEditor(QtWidgets.QLineEdit):
    def __init__(self, content, parent=None):
        super().__init__(content, parent=parent)

class FeedbackConfiguration(QtCore.QObject):
    triggerEnabled = QtCore.pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._enable = QtWidgets.QCheckBox("Enable trigger")
        self._header = QtWidgets.QLabel("Trigger UDP port: ")
        self._field  = PortEditor("6666")
        self._tester = QtWidgets.QPushButton("Toggle Manually")
        self._tester.setCheckable(True)
        self._tester.setChecked(False)
        self._enable.stateChanged.connect(self.update)
        self.setTriggerable(False)

    @property
    def enablebutton(self):
        return self._enable

    @property
    def header(self):
        return self._header

    @property
    def port(self):
        return self._field

    @property
    def test(self):
        return self._tester

    def setTriggerable(self, val: bool):
        self._enable.setEnabled(val)
        self.update()

    def update(self, notused=None):
        status = self._enable.isEnabled() and (self._enable.checkState() != QtCore.Qt.Unchecked)
        self._tester.setEnabled(not status)
        self.triggerEnabled.emit(status)

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
from .expression import parse as _parse_expression, \
                        ParseError as _ParseError

class NotDLCProjectError(ValueError):
    def __init__(self, msg):
        super().__init__(msg)

class EvaluationControl(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__("DeepLabCut Evaluation", parent=parent)
        self._loader   = ProjectSelector("DLC Project: ")
        self._expr     = EvaluationEditor()
        self.DLCProjectChanged = self._loader.projectChanged
        self.evaluationEnabled = self._expr.evaluationEnabled
        self.expressionChanged = self._expr.expressionChanged

        self.updateWithBodyParts  = self._expr.updateWithBodyParts
        self.cancelLoadingProject = self._loader.cancelLoadingProject
        self._loader.projectChanged.connect(self._expr.updateWithProject)

        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._loader.header, 1, 0)
        self._layout.addWidget(self._loader.field,  1, 1)
        self._layout.addWidget(self._loader.loadbutton, 1, 2)
        self._layout.addWidget(self._loader.clearbutton, 1, 3)
        self._layout.addWidget(self._expr.partdisplay, 2, 0, 1, 4)
        self._layout.addWidget(self._expr.enablebutton, 3, 0, 1, 4)
        self._layout.addWidget(self._expr.header, 4, 0)
        self._layout.addWidget(self._expr.editor, 4, 1, 1, 3)
        self.setLayout(self._layout)

    def disableAllControls(self):
        for elem in (self._loader.header,
                     self._loader.field,
                     self._loader.loadbutton,
                     self._loader.clearbutton,
                     self._expr.partdisplay,
                     self._expr.enablebutton,
                     self._expr.header,
                     self._expr.editor):
            elem.setEnabled(False)
        self.setTitle("DeepLabCut Evaluation (disabled)")

    def lockControl(self, val: bool):
        self._loader.setEnabled(not val)
        self._expr.enablebutton.setEnabled(not val)

class ProjectSelector(QtCore.QObject):
    """the object for selecting DLC project."""
    projectChanged    = QtCore.pyqtSignal(str)

    NOT_SELECTED   = "<not selected>"

    def __init__(self, labeltext: str, parent=None):
        super().__init__(parent=parent)
        self._header = QtWidgets.QLabel(labeltext)
        self._field  = QtWidgets.QLabel(self.NOT_SELECTED)
        self._load   = QtWidgets.QPushButton("Select...")
        self._clear  = QtWidgets.QPushButton("Clear")
        self._path   = None

        self._load.clicked.connect(self.selectProjectByDialog)
        self._clear.clicked.connect(self.confirmClear)
        self.updateUI()

    def setEnabled(self, val: bool):
        for widget in (self._header, self._field, self._load, self._clear):
            widget.setEnabled(val)

    @property
    def header(self):
        return self._header

    @property
    def field(self):
        return self._field

    @property
    def loadbutton(self):
        return self._load

    @property
    def clearbutton(self):
        return self._clear

    def confirmClear(self):
        # TODO: prompt confirmation
        self.setProject(None)

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
        if path is not None:
            path = Path(path)
            # validate
            if not (path / "config.yaml").exists():
                raise NotDLCProjectError(f"'{path.name}' does not seem to be a DLC project")
        else:
            pass
        self._path = path
        self.updateUI()
        self.projectChanged.emit(str(path) if path is not None else "")

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

    def cancelLoadingProject(self, errorTitle, errorMsg):
        QtWidgets.QMessageBox.warning(self._field, errorTitle, errorMsg)
        self.setProject(None)

class EvaluationEditor(QtCore.QObject):
    evaluationEnabled = QtCore.pyqtSignal(bool)
    expressionChanged = QtCore.pyqtSignal(object, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._bodyparts  = []
        self._partdisplay = QtWidgets.QLabel("Body parts: <none>")
        self._enable = QtWidgets.QCheckBox("Enable evaluation")
        self._enable.setCheckState(QtCore.Qt.Unchecked)
        self._header = QtWidgets.QLabel("Expression: ")
        self._field  = QtWidgets.QLineEdit()

        self._enable.stateChanged.connect(self.updateUI)
        self._field.returnPressed.connect(self.updateWithExpression)
        # self.setEnabled(False)

    @property
    def partdisplay(self):
        return self._partdisplay

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

    def updateWithBodyParts(self, parts):
        self._bodyparts = parts
        displayed = "<none>" if len(parts) == 0 else ", ".join(str(part) for part in parts)
        self._partdisplay.setText(f"Body parts: {displayed}")

    def updateWithExpression(self):
        content = self._field.text()
        if len(content.strip()) == 0:
            expr = None
            self._field.setStyleSheet("color: black")
        else:
            try:
                expr = _parse_expression(content, self._bodyparts)
                self._field.setStyleSheet("color: black")
            except _ParseError as e:
                QtWidgets.QMessageBox.warning(self._field, "Failed to update expression", f"{e}")
                self._field.setStyleSheet("color: red")
                return
        self.expressionChanged.emit(expr, content)

    def setEnabled(self, val: bool):
        self._enable.setEnabled(val)
        self.updateUI()

    def updateUI(self, value=None):
        """value: not used"""
        status = self._enable.isEnabled() and (self._enable.checkState() == QtCore.Qt.Checked)
        for widget in (self._header, self._field):
            widget.setEnabled(status)
        self.evaluationEnabled.emit(status)

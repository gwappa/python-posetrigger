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

class EvaluationControl(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Evaluation", parent=parent)
        self._view   = None
        self._loader = ProjectSelector("DLC Project: ")
        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._loader.header, 1, 0)
        self._layout.addWidget(self._loader.field,  1, 1)
        self._layout.addWidget(self._loader.loadbutton, 1, 2)
        self.setLayout(self._layout)

class ProjectSelector(QtWidgets.QWidget):
    """the widget for selecting DLC project."""
    projectChanged = QtCore.pyqtSignal(str)
    NOT_SELECTED   = "<not selected>"

    def __init__(self, labeltext: str, parent=None):
        super().__init__(parent=parent)
        self._header = QtWidgets.QLabel(labeltext)
        self._field  = QtWidgets.QLabel(self.NOT_SELECTED)
        self._load   = QtWidgets.QPushButton("Select...")
        self._path   = None

        self._load.clicked.connect(self.selectProjectByDialog)

        self._layout = QtGui.QHBoxLayout()
        for widget in (self._header, self._field, self._load):
            self._layout.addWidget(widget)
        self.setLayout(self._layout)
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
        path = QtWidgets.QFileDialog.getExistingDirectory(self,
                                        "Select a DeepLabCut project...",
                                        "",
                                        QtWidgets.QFileDialog.ShowDirsOnly)
        try:
            self.setProject(path)
        except NotDLCProjectError as e:
            QtWidgets.QMessageBox.warning(self, "Failed to select the directory", f"{e}")

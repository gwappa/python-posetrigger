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
from . import debug as _debug

class PreprocessingControl(QtWidgets.QGroupBox):
    valueChanged = QtCore.pyqtSignal(int)

    def __init__(self, initial=65535, parent=None):
        super().__init__("Live preview", parent=parent)
        self._layout = QtGui.QGridLayout()
        self._scale  = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._field  = QtWidgets.QSpinBox()
        self._value  = initial
        self._updating = False

        self._scale.setTickPosition(QtWidgets.QSlider.NoTicks)
        self._scale.setMinimum(1)
        self._scale.setMaximum(65535)
        self._scale.setValue(initial)
        self._scale.valueChanged.connect(self.updateWithSlider)

        self._field.setMinimum(1)
        self._field.setMaximum(65535)
        self._field.setValue(initial)
        self._field.valueChanged.connect(self.updateWithField)

        self._layout.addWidget(QtWidgets.QLabel("Lightness range"), 0, 0)
        self._layout.addWidget(self._scale, 0, 1)
        self._layout.addWidget(self._field, 0, 2)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 2)
        self._layout.setColumnStretch(2, 1)
        self.setLayout(self._layout)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self.valueChanged.emit(val)

    def updateWithSlider(self, val):
        if self._updating == False:
            self._updating = True
            self.value     = val
            self._field.setValue(val)
            self._updating = False

    def updateWithField(self, val):
        if self._updating == False:
            self._updating = True
            self.value     = val
            self._scale.setValue(val)
            self._updating = False

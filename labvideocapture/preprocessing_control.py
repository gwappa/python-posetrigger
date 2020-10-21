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

class IntValueModel(QtCore.QObject):
    """validatable int value model."""
    valueChanged = QtCore.pyqtSignal(int)
    def __init__(self, initial, bounds=(0, 255), parent=None):
        super().__init__(parent=parent)
        self._value  = initial
        self._bounds = tuple(sorted(bounds))

    def validate(self, value: int):
        if value < self._bounds[0]:
            return self._bounds[0]
        elif value > self._bounds[1]:
            return self._bounds[1]
        return value

    @property
    def bounds(self):
        return self._bounds

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value: int):
        value = self.validate(value)
        if (value != self._value):
            self._value = value
            self.valueChanged.emit(value)

class IntRangeModel(QtCore.QObject):
    rangeChanged = QtCore.pyqtSignal(int, int)
    def __init__(self, initialMin, initialMax, bounds=(0, 255), parent=None):
        super().__init__(parent=parent)
        self._lower = IntValueModel(initialMin, bounds=bounds)
        self._upper = IntValueModel(initialMax, bounds=bounds)

        self._lower.validate = self.validateLowerBound
        self._upper.validate = self.validateUpperBound
        self._lower.valueChanged.connect(self.lowerBoundChanged)
        self._upper.valueChanged.connect(self.upperBoundChanged)

    def validateLowerBound(self, value: int):
        if value >= self._upper.value:
            return self._upper.value - 1
        else:
            return IntValueModel.validate(self._lower, value)

    def validateUpperBound(self, value: int):
        if value <= self._lower.value:
            return self._lower.value + 1
        else:
            return IntValueModel.validate(self._upper, value)

    def lowerBoundChanged(self, value: int):
        self.rangeChanged.emit(value, self._upper.value)

    def upperBoundChanged(self, value: int):
        self.rangeChanged.emit(self._lower.value, value)

    @property
    def lower(self):
        return self._lower

    @property
    def upper(self):
        return self._upper

class IntSliderView(QtWidgets.QSlider):
    def __init__(self, model, orientation=QtCore.Qt.Horizontal, parent=None):
        super().__init__(orientation, parent=parent)
        min, max = model.bounds
        self.setMinimum(min)
        self.setMaximum(max)
        self.setValue(model.value)
        self._model    = model
        self._updating = False
        self._model.valueChanged.connect(self.updateWithModel)
        self.valueChanged.connect(self.updateWithView)
        self.sliderReleased.connect(self.ensureSliderPosition)

    def updateWithModel(self, value: int):
        self._updating = True
        self.setSliderPosition(value)
        self._updating = False

    def updateWithView(self, value: int):
        if self._updating == False:
            self._model.value = value

    def ensureSliderPosition(self):
        self.updateWithModel(self._model.value)

class IntFieldView(QtWidgets.QLineEdit):
    def __init__(self, model, parent=None):
        super().__init__(parent=parent)
        self.setText(str(model.value))
        self._model   = model
        self._updating = False
        self._model.valueChanged.connect(self.updateWithModel)
        self.returnPressed.connect(self.updateWithView)

    def updateWithModel(self, value: int):
        self._updating = True
        self.setText(str(value))
        self._updating = False

    def updateWithView(self):
        if self._updating == False:
            try:
                self._model.value = int(self.text())
                return
            except ValueError:
                pass
            # roll back to the original value, in case of any error
            self.setText(str(self._model.value))

class DefaultIntEdit(QtCore.QObject):
    def __init__(self, title, model, parent=None):
        super().__init__(parent=parent)
        self._header = QtWidgets.QLabel(title)
        self._slider = IntSliderView(model)
        self._field  = IntFieldView(model)
        self.setTickPosition = self._slider.setTickPosition

    @property
    def header(self):
        return self._header

    @property
    def slider(self):
        return self._slider

    @property
    def field(self):
        return self._field

class PreprocessingControl(QtWidgets.QGroupBox):

    def __init__(self, initial=(0, 65535), bounds=(0, 65535), parent=None):
        super().__init__("Preprocessing", parent=parent)
        lower, upper = tuple(sorted(initial))
        self._range  = IntRangeModel(lower, upper, bounds=bounds)
        self._lower  = DefaultIntEdit("Min. lightness", self._range.lower)
        self._upper  = DefaultIntEdit("Max. lightness", self._range.upper)
        self._notes  = QtWidgets.QLabel("(Raw images are used for storage)")
        self.rangeChanged = self._range.rangeChanged

        for view in (self._lower, self._upper):
            view.setTickPosition(QtWidgets.QSlider.NoTicks)

        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._lower.header, 0, 0)
        self._layout.addWidget(self._lower.slider, 0, 1)
        self._layout.addWidget(self._lower.field,  0, 2)
        self._layout.addWidget(self._upper.header, 1, 0)
        self._layout.addWidget(self._upper.slider, 1, 1)
        self._layout.addWidget(self._upper.field,  1, 2)
        self._layout.addWidget(self._notes,      2, 0, 1, 3)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 2)
        self._layout.setColumnStretch(2, 1)
        self.setLayout(self._layout)

    @property
    def range(self):
        return (self._range.lower.value, self._range.upper.value)

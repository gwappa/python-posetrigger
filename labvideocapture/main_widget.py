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
from . import camera_interface as _camera
from . import evaluation as _eval
from . import acquisition_control as _actrl
from . import storage_control as _sctrl
from . import evaluation_control as _ectrl
from . import trigger_control as _tctrl
from . import frame_view as _fview

from . import debug as _debug

class MainWidget(QtGui.QWidget):
    """the main GUI consisting of camera interface, frame view and acquisition interface."""
    def __init__(self, path="/dev/video0", parent=None):
        super().__init__(parent)
        self._device     = _camera.load_device(path)
        self._camera     = _camera.CameraInterface(self._device)
        self._control    = _actrl.AcquisitionControl(self._device)
        self._storage    = _sctrl.StorageControl()
        self._evalmodel  = _eval.Evaluation()
        self._evaluation = _ectrl.EvaluationControl()
        self._trigger    = _tctrl.TriggerControl()
        self._frame      = _fview.FrameView(self._camera.width, self._camera.height)
        self._connectComponents()
        self._layout  = QtGui.QGridLayout()
        self._layout.addWidget(self._frame,      0, 0, 4, 1)
        self._layout.addWidget(self._camera,     0, 1, 1, 2)
        self._layout.addWidget(self._control,    1, 1, 1, 2)
        self._layout.addWidget(self._evaluation, 2, 1, 1, 2)
        self._layout.addWidget(self._trigger,    3, 1, 1, 2)
        self._layout.addWidget(self._storage,    4, 1, 1, 2)
        self._layout.addWidget(self._control.statuslabel, 5, 0)
        self._layout.addWidget(self._control.focusbutton, 5, 1)
        self._layout.addWidget(self._control.acquirebutton, 5, 2)
        self._layout.setColumnStretch(1, -1)
        self._layout.setColumnStretch(2, -1)
        self._layout.setColumnStretch(0, 1)
        self._layout.setRowStretch(0, 2)
        self._layout.setRowStretch(1, 2)
        self._layout.setRowStretch(2, 2)
        self._layout.setRowStretch(3, 2)
        self._layout.setRowStretch(4, 2)
        self._layout.setRowStretch(5, 1)
        self.setLayout(self._layout)
        self.setWindowTitle("LabVideoCapture")
        self.resize(1050,720)

    def _connectComponents(self):
        self._control.modeIsChanging.connect(self._frame.update_with_acquisition_mode)
        self._control.modeIsChanging.connect(self._storage.update_with_acquisition_mode)
        self._storage.statusUpdated.connect(self._control.show_storage_status)

        self._connectEvaluationToModel()
        self._connectEvaluationToTrigger()
        self._connectTriggerToModel()

    def _connectEvaluationToModel(self):
        self._evaluation.DLCProjectChanged.connect(self._evalmodel.updateWithProject)
        self._evaluation.evaluationEnabled.connect(self._evalmodel.setEvaluationEnabled)
        self._evaluation.expressionChanged.connect(self._evalmodel.setExpression)
        self._evalmodel.bodypartsUpdated.connect(self._evaluation.updateWithBodyParts)
        self._evalmodel.errorOccurredOnLoading.connect(self._evaluation.cancelLoadingProject)

    def _connectEvaluationToTrigger(self):
        self._evaluation.evaluationEnabled.connect(self._trigger.setTriggerable)

    def _connectTriggerToModel(self):
        self._evalmodel.statusUpdated.connect(self._trigger.updateOutput)

    @property
    def camera(self):
        return self._camera

    @property
    def acquisition(self):
        return self._acq

    @property
    def frame(self):
        return self._frame

    def teardown(self):
        self._camera.teardown()
        self._storage.teardown()

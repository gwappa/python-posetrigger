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
from . import preprocessing_control as _pctrl

from . import debug as _debug
from . import InitializationError as _Error

WIDGET_NAME = "Pose-Trigger"

class MainWidget(QtGui.QWidget):
    """the main GUI consisting of camera interface, frame view and acquisition interface."""
    def __init__(self, path="/dev/video0", parent=None):
        super().__init__(parent)
        try:
            self._device     = _camera.load_device(path)
            msg = ""
        except RuntimeError as e:
            msg = f"{e}"
            self._device = None
        if self._device is None:
            raise _Error(f"failed to initialize the device '{path}', please make sure you point to the correct device:\n   {msg}")
        self._camera     = _camera.CameraInterface(self._device)
        self._control    = _actrl.AcquisitionControl(self._device)
        self._storage    = _sctrl.StorageControl()
        self._evalmodel  = _eval.Evaluation()
        self._evaluation = _ectrl.EvaluationControl()
        self._trigger    = _tctrl.TriggerControl()
        self._frame      = _fview.FrameView(self._camera.width, self._camera.height)
        self._processing = _pctrl.PreprocessingControl()

        if not self._evalmodel.HAS_DLC:
            QtWidgets.QMessageBox.warning(self, "Failed to load DeepLabCut",
                """LabVideoCapture failed to import "dlclib".
The evaluation functionality will be disabled.

To enable it, install DeepLabCut (version >=1.11) and DLCLib (version >=1.0.2), and launch LabVideoCapture again.""")
            self._evaluation.disableAllControls()

        self._connectComponents()
        self._layout  = QtGui.QGridLayout()
        self._layout.addWidget(self._frame,      0, 0, 6, 1)
        self._layout.addWidget(self._camera,     0, 1, 1, 2)
        self._layout.addWidget(self._processing, 1, 1, 1, 2)
        self._layout.addWidget(self._control,    2, 1, 1, 2)
        self._layout.addWidget(self._evaluation, 3, 1, 1, 2)
        self._layout.addWidget(self._trigger,    4, 1, 1, 2)
        self._layout.addWidget(self._storage,    5, 1, 1, 2)
        self._layout.addWidget(self._control.statuslabel, 6, 0)
        self._layout.addWidget(self._control.focusbutton, 6, 1)
        self._layout.addWidget(self._control.acquirebutton, 6, 2)
        self._layout.setColumnStretch(1, -1)
        self._layout.setColumnStretch(2, -1)
        self._layout.setColumnStretch(0, 1)
        self._layout.setRowStretch(0, 2)
        self._layout.setRowStretch(1, 1)
        self._layout.setRowStretch(2, 1)
        self._layout.setRowStretch(3, 2)
        self._layout.setRowStretch(4, 2)
        self._layout.setRowStretch(5, 2)
        self._layout.setRowStretch(6, 1)
        self.setLayout(self._layout)
        self.setWindowTitle(WIDGET_NAME)
        self.resize(1200,720)

    def _connectComponents(self):
        self._control.modeIsChanging.connect(self._camera.updateWithAcquisition)
        self._control.modeIsChanging.connect(self._frame.updateWithAcquisition)
        self._control.modeIsChanging.connect(self._storage.updateWithAcquisition)
        self._control.modeIsChanging.connect(self._evalmodel.updateWithAcquisition)
        self._control.modeIsChanging.connect(self._trigger.updateWithAcquisition)
        self._storage.statusUpdated.connect(self._control.show_storage_status)

        vmin, vmax = self._processing.range
        self._frame.setRange(vmin, vmax)
        self._evalmodel.setLightnessRange(vmin, vmax)
        self._processing.rangeChanged.connect(self._frame.setRange)
        self._processing.rangeChanged.connect(self._evalmodel.setLightnessRange)

        self._connectEvaluationToModel()
        self._connectEvaluationToFrame()
        self._connectEvaluationToTrigger()
        self._connectEvaluationModelToStorage()

    def _connectEvaluationToFrame(self):
        self._evalmodel.bodypartsUpdated.connect(self._frame.registerBodyParts)

    def _connectEvaluationToModel(self):
        self._evaluation.DLCProjectChanged.connect(self._evalmodel.updateWithProject)
        self._evaluation.evaluationEnabled.connect(self._evalmodel.setEvaluationEnabled)
        self._evaluation.expressionChanged.connect(self._evalmodel.setExpression)
        self._evalmodel.evaluationModeLocked.connect(self._evaluation.lockControl)
        self._evalmodel.bodypartsUpdated.connect(self._evaluation.updateWithBodyParts)
        self._evalmodel.errorOccurredOnLoading.connect(self._evaluation.cancelLoadingProject)

    def _connectEvaluationToTrigger(self):
        self._evaluation.evaluationEnabled.connect(self._trigger.setTriggerable)

    def _connectEvaluationModelToStorage(self):
        self._evalmodel.bodypartsUpdated.connect(self._storage.updateWithBodyParts, QtCore.Qt.QueuedConnection)

    @property
    def camera(self):
        return self._camera

    @property
    def frame(self):
        return self._frame

    def teardown(self):
        self._storage.teardown()
        self._trigger.teardown()
        self._camera.teardown() # has to be the last as it can cause seg fault

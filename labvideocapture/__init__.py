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

VERSION_STR = "0.1.0"

from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
import numpy as _np
from skvideo.io import FFmpegWriter as _FFmpegWriter
import pyqtgraph as _pg
import timedcapture as _cap

DEBUG = True

def debug(msg, end="\n"):
    import sys
    if DEBUG == True:
        print(msg, end=end, file=sys.stderr, flush=True)

def image_to_display(img):
    if img.ndim == 3:
        return img.transpose((1,0,2))
    else:
        return img.T

class MainView(QtGui.QWidget):
    """the main GUI consisting of camera interface, frame view and acquisition interface."""
    def __init__(self, path="/dev/video0", parent=None):
        super().__init__(parent)
        self._device = _cap.Device(path)
        self._runner = Acquisition(self._device)
        self._runner.start()
        self._camera = CameraInterface(self._device)
        self._acq    = AcquisitionInterface(self._runner)
        self._frame  = FrameView(self.camera.width, self.camera.height)
        self._runner.frameAcquired.connect(self._frame.update_with_image)
        self._layout = QtGui.QGridLayout()
        self._layout.addWidget(self._frame, 0, 0, 2, 1)
        self._layout.addWidget(self._camera, 0, 1, 1, 2)
        self._layout.addWidget(self._acq,    1, 1, 1, 2)
        self._layout.addWidget(self._acq.statuslabel, 2, 0)
        self._layout.addWidget(self._acq.focusbutton, 2, 1)
        self._layout.addWidget(self._acq.acquirebutton, 2, 2)
        self._layout.setColumnStretch(1, 1)
        self._layout.setColumnStretch(2, 1)
        self._layout.setColumnStretch(0, -1)
        self._layout.setRowStretch(0, 5)
        self._layout.setRowStretch(1, 5)
        self._layout.setRowStretch(2, 1)
        self.setLayout(self._layout)
        self.setWindowTitle("LabVideoCapture")
        self.resize(960,540)

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
        self._runner.teardown()
        self._runner.wait()

class FrameView(QtWidgets.QGraphicsView):
    """a thin wrapper class that is used to display acquired frames.
    the `update_with_image` method updates what is displayed.
    """
    def __init__(self, width, height, parent=None):
        super().__init__(parent=parent)
        self._width  = width
        self._height = height
        self._scene  = QtWidgets.QGraphicsScene()
        self._image  = _pg.ImageItem(_np.zeros((width,height), dtype=_np.uint16))

        self.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._scene.addItem(self._image)
        self.setScene(self._scene)

    def update_with_image(self, img):
        self._image.setImage(image_to_display(img))

class CameraInterface(QtGui.QGroupBox):
    """the UI for the control of exposure/gain of the device to be used.
    it has path/width/height properties to refer to (but fixed)."""
    def __init__(self, device, parent=None):
        super().__init__(f"Camera '{device.path}'", parent=parent)
        self._device   = device

        self._exposure = QtGui.QSpinBox()
        self._exposure.setSuffix("us")
        self._exposure.setMinimum(1)
        self._exposure.setMaximum(1000000)
        self._exposure.setValue(self._device.exposure_us)
        self._exposure.valueChanged.connect(self.update_exposure)

        self._gain     = QtGui.QSpinBox()
        self._gain.setMinimum(0)
        self._gain.setMaximum(480)
        self._gain.setValue(self._device.gain)
        self._gain.valueChanged.connect(self.update_gain)

        self._layout = QtGui.QFormLayout()
        self._layout.addRow("exposure", self._exposure)
        self._layout.addRow("gain", self._gain)
        self.setLayout(self._layout)

    @property
    def path(self):
        return self._device.path

    @property
    def width(self):
        return self._device.width

    @property
    def height(self):
        return self._device.height

    def update_exposure(self, value):
        self._device.exposure_us = int(value)

    def update_gain(self, value):
        self._device.gain = int(value)

class Acquisition(QtCore.QThread):
    statusUpdated = QtCore.pyqtSignal(bool)
    frameAcquired = QtCore.pyqtSignal(_np.ndarray)

    def __init__(self, device, parent=None):
        super().__init__(parent=parent)
        self._device  = device
        self._control = QtCore.QMutex()
        self._capture = False
        self._signal  = False
        self._update  = QtCore.QWaitCondition()

    @property
    def capturing(self):
        self._control.lock()
        val = self._capture
        self._control.unlock()
        return val

    @property
    def signaled(self):
        self._control.lock()
        val = self._signal
        self._control.unlock()
        return val

    @capturing.setter
    def capturing(self, val):
        self._control.lock()
        if self._capture == val:
            self._control.unlock()
            return
        if val == True:
            self._device.start_capture()
        else:
            val = False
            self._device.stop_capture()
        self._capture = val
        self.statusUpdated.emit(val)
        self._update.wakeAll()
        self._control.unlock()
        QtCore.QCoreApplication.processEvents()

    def run(self):
        self._control.lock()
        while True:
            self._update.wait(self._control)
            if self._signal == True:
                self._control.unlock()
                debug("terminating the acquisition thread.")
                break
            elif self._capture == True:
                self._control.unlock()
                while True:
                    if self.read_single() is None:
                        debug(f"pausing acquisition.")
                        break

    def read_single(self):
        self._control.lock()
        if self._capture == False:
            debug(f"Acquisition: stop seems to have been requested.")
            return None
        frame = self._device.read_frame()
        self.frameAcquired.emit(frame)
        self._control.unlock()
        return frame

    def start_capture(self):
        self.capturing = True

    def stop_capture(self):
        self.capturing = False

    def teardown(self):
        self._control.lock()
        self._signal  = True
        self._capture = False
        self._update.wakeAll()
        self._control.unlock()

class AcquisitionInterface(QtGui.QGroupBox):
    statusUpdated  = QtCore.pyqtSignal(str)
    starting       = QtCore.pyqtSignal()
    stopping       = QtCore.pyqtSignal()

    def __init__(self, model, parent=None):
        super().__init__("Acquisition", parent=None)
        self._model    = model
        self._mode     = "" # holds the current mode
        self._storage  = None
        self.starting.connect(self._model.start_capture, type=QtCore.Qt.QueuedConnection)
        self.stopping.connect(self._model.stop_capture, type=QtCore.Qt.QueuedConnection)
        self._model.statusUpdated.connect(self.update_with_model, type=QtCore.Qt.QueuedConnection)

        self._filepath = QtGui.QLineEdit("out.mp4")
        self._focus    = RunButton("FOCUS")
        self._focus.startRequested.connect(self.start_focus)
        self._focus.stopRequested.connect(self.stop_focus)
        self._acquire  = RunButton("ACQUIRE")
        self._acquire.startRequested.connect(self.start_acquisition)
        self._acquire.stopRequested.connect(self.stop_acquisition)
        self.statusUpdated.connect(self._focus.set_status)
        self.statusUpdated.connect(self._acquire.set_status)

        self._label    = QtGui.QLabel("")

        self._layout = QtGui.QFormLayout()
        self._layout.addRow("output file path", self._filepath)
        self.setLayout(self._layout)

    @property
    def focusbutton(self):
        return self._focus

    @property
    def acquirebutton(self):
        return self._acquire

    @property
    def statuslabel(self):
        return self._label

    def update_with_model(self, running):
        if running == True:
            pass
        else:
            if self._mode == "ACQUIRE":
                self._storage.close()
                self._model.frameAcquired.disconnect(self._storage.write)
                self._storage = None
            self._mode = ""
        self._label.setText("")
        self.statusUpdated.emit(self._mode)

    def start_focus(self):
        self._mode = "FOCUS"
        self.starting.emit()

    def stop_focus(self):
        self._mode = "FOCUS"
        self._focus.setEnabled(False)
        self._label.setText("terminating the FOCUS mode...")
        QtCore.QCoreApplication.processEvents()
        self.stopping.emit()

    def start_acquisition(self):
        self._mode = "ACQUIRE"
        self._storage = DefaultVideoWriter(self._filepath.text())
        self._model.frameAcquired.connect(self._storage.write, type=QtCore.Qt.QueuedConnection)
        self.starting.emit()

    def stop_acquisition(self):
        self._mode = "ACQUIRE"
        self._acquire.setEnabled(False)
        self._label.setText("terminating the ACQUIRE mode...")
        QtCore.QCoreApplication.processEvents()
        self.stopping.emit()

class RunButton(QtGui.QPushButton):
    startRequested = QtCore.pyqtSignal()
    stopRequested  = QtCore.pyqtSignal()

    def __init__(self, title, alt_title="STOP", parent=None):
        super().__init__(title, parent=parent)
        self._basetext = title
        self._alttext  = alt_title
        self.setCheckable(True)
        self.clicked.connect(self.emit_request)

    def emit_request(self, checked):
        if self.text() == self._basetext:
            debug(f"starting: {self._basetext}")
            self.startRequested.emit()
        else:
            debug(f"stopping: {self._basetext}")
            self.stopRequested.emit()
        # wait for the other processes to update the status
        self.setChecked(not checked)

    def set_status(self, status):
        if status == self._basetext:
            debug(f"{self._basetext} started")
            self.setEnabled(True)
            self.setText(self._alttext)
            self.setChecked(True)
        elif len(status) == 0:
            debug(f"{self._basetext}: reverting to base status")
            self.setEnabled(True)
            self.setText(self._basetext)
            self.setChecked(False)
        else:
            debug(f"disabling {self._basetext}")
            self.setEnabled(False)

class DefaultVideoWriter(QtCore.QObject):
    def __init__(self, path, parent=None):
        super().__init__(parent=parent)
        inputs = {"-input_format": "gray16le"}
        outputs = {"-c:v": "libx264"}
        self._out = _FFmpegWriter(path, inputdict=inputs, outputdict=outputs)
        debug(f"opened a writer for: {path}")

    def write(self, frame):
        frame = _np.array(frame, copy=True)
        self._out.writeFrame(frame)

    def close(self):
        if self._out is not None:
            self._out.close()
        self._out = None

def run_main(camera_path="/dev/video0"):
    app    = QtGui.QApplication([])
    window = MainView(path=camera_path)
    app.aboutToQuit.connect(window.teardown)
    window.show()
    QtGui.QApplication.instance().exec_()

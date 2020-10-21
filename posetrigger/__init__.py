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
import argparse as _ap
from pathlib import Path as _Path

parser = _ap.ArgumentParser(description="real-time capture and closed-loop triggering program.")
parser.add_argument("device", default="/dev/video0",
    help="the path to the V4L2-compliant (preferrably ImagingSource) capture device.")

VERSION_STR = "1.0.0"

DEBUG = True

def debug(msg, end="\n"):
    import sys
    if DEBUG == True:
        print(msg, end=end, file=sys.stderr, flush=True)

def main():
    run(**vars(parser.parse_args()))

def run(device="/dev/video0"):
    if not _Path(device).exists():
        print(f"***device does not exist: {device}")
        return
    from .main_widget import MainWidget
    from pyqtgraph.Qt import QtGui
    app    = QtGui.QApplication([])
    window = MainWidget(path=device)
    app.aboutToQuit.connect(window.teardown)
    window.show()
    QtGui.QApplication.instance().exec_()
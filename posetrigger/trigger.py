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

import socket as _socket
import struct as _struct
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from . import debug as _debug

API_MSG_SIZE = 2
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 11666

def from_byte_to_int(byte):
    return int.from_bytes(byte, 'big')

def from_int_to_byte(val):
    return val.to_bytes(1, 'big')

class Commands:
    """the commands to send to the server."""
    SYNC  = b'\x10'
    EVENT = b'\x20'
    CLEAR = b'\x00'
    QUIT  = b'\x03'

class Packet:
    """a packet for FastEventServer API."""
    def __init__(self):
        self.__codec = _struct.Struct('Bc')

    def encode(self, index, sync=None, event=None, shutdown=False):
        """returns a 2-byte command"""
        code = int.from_bytes(Commands.CLEAR, 'big')
        for flag, cmd in ((sync, Commands.SYNC),
                        (event, Commands.EVENT),
                        (shutdown, Commands.QUIT)):
            if flag == True:
                code |= from_byte_to_int(cmd)
        return self.__codec.pack(index, from_int_to_byte(code))

    def decode(self, msg):
        """returns (index, sync, event) in a tuple."""
        index, state = self.__codec.unpack(msg)
        code = from_byte_to_int(state)
        ret  = (index,)
        for cmd in (Commands.SYNC, Commands.EVENT):
            flag = from_byte_to_int(cmd)
            ret += ((code & flag != 0),)
        return ret

class Client:
    def __init__(self, host=None, port=None):
        self._host = host if host is not None else DEFAULT_HOST
        self._port = port if port is not None else DEFAULT_PORT
        self._sock = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        self._sock.settimeout(0.1)
        self._sock.connect((self._host, self._port))

        self._sync   = False
        self._event  = False
        self._idx    = 0
        self._packet = Packet()
        self.clear()

    def communicate(self, sync=None, event=None, shutdown=False):
        if sync is None:
            sync = self._sync
        if event is None:
            event = self._event
        try:
            self._sock.sendall(self._packet.encode(self._idx,
                                                   sync=sync, event=event, shutdown=shutdown))
        except OSError:
            raise RuntimeError("Message rejected")

        idx, self._sync, self._event = self._packet.decode(self._sock.recv(API_MSG_SIZE))
        assert(self._idx == idx)
        self._idx += 1
        if self._idx == 256:
            self._idx = 0
        #_debug(f"sync={self._sync}, event={self._event}, shutdown={shutdown}")

    def close(self):
        self._sock.close()
        self._sock = None

    def clear(self):
        self.communicate(event=False, sync=False)

    def shutdown(self):
        self.communicate(shutdown=True)
        self.close()

    @property
    def sync(self):
        return self._sync

    @sync.setter
    def sync(self, val: bool):
        self.communicate(sync=val)

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, val: bool):
        self.communicate(event=val)

class TriggerOutput(QtCore.QObject):
    def __init__(self, port, parent=None):
        super().__init__(parent=parent)
        self._triggered = False
        self._acq       = None
        self._conn      = Client(port=port)

    @property
    def enabled(self):
        return self._triggered

    @enabled.setter
    def enabled(self, val: bool):
        self._triggered = val
        if self._acq is not None:
            self._acq.setTriggerOutput(self.updateOutput if val == True else None)

    def updateWithAcquisition(self, mode, acq):
        if mode != "":
            # starting
            self._acq = acq
            acq.setTriggerOutput(self.updateOutput if self._triggered == True else None)
            if mode == "ACQUIRE":
                self._conn.sync = True

            acq.setStaticMetadata("trigger", self._triggered)
        else:
            # ending
            self._acq = None
            self._conn.sync = False

    def updateOutput(self, val: bool):
        self._conn.event = val

    def teardown(self):
        try:
            self._conn.shutdown()
        except:
            pass

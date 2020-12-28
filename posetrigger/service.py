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

from pathlib import Path as _Path
import time as _time
import subprocess as _sp
import json as _json

CONFIG_PATH = _Path.home() / ".fasteventserver-config"
DEFAULT_DRIVER = "dummy"
DEFAULT_PORT   = 11666
DEFAULT_DEVICE = "/dev/ttyACM0"
DEFAULT_CONFIG = {
    "port": DEFAULT_PORT,
    "driver": "leonardo",
    "options": {
        "port": DEFAULT_DEVICE
    }
}

BINARY_DIR = _Path(__file__).parent / "bin"

config = None

def get_cpu_arch():
    src = _sp.run(["lscpu"], capture_output=True, check=True).stdout.decode("utf-8")
    tag  = "Architecture:"
    for line in src.split("\n"):
        if line.startswith(tag):
            return line.replace(tag, "").strip()
    raise RuntimeError("failed to find the architecture info")

def get_binary_path():
    arch = get_cpu_arch()
    path = BINARY_DIR / f"FastEventServer_linux_{arch}"
    if not path.exists():
        raise FileNotFoundError(f"FastEventServer binary for the architecture '{arch}' does not exist")
    return path

def initialize():
    global config
    if config is None:
        config = load()
    if "driver" not in config.keys():
        print(f"***key 'driver' not found in '{CONFIG_PATH}': '{DEFAULT_DRIVER}' is used as the default.")
        config["driver"] = DEFAULT_DRIVER
    if "port" not in config.keys():
        print(f"***key 'port' not found in '{CONFIG_PATH}': '{DEFAULT_PORT}' is used as the default.")
        config["port"] = DEFAULT_PORT
    if "options" not in config.keys():
        config["options"] = {}
    if "port" not in config["options"].keys():
        print(f"***key 'options/port' not found in '{CONFIG_PATH}': '{DEFAULT_DEVICE}' is used as the default.")
        config["options"]["port"] = DEFAULT_DEVICE
    # in case of any updates
    update()

proc = None

def get_driver_type():
    global config
    if config is None:
        initialize()
    return config["driver"]

def set_driver_type(value):
    global config
    if config is None:
        initialize()
    config["driver"] = str(value)
    update()

def get_udp_port():
    global config
    if config is None:
        initialize()
    return config["port"]

def set_udp_port(value):
    global config
    if config is None:
        initialize()
    config["port"] = int(value)
    update()

def get_serial_port():
    global config
    if config is None:
        initialize()
    return config["options"]["port"]

def set_serial_port(value):
    global config
    if config is None:
        initialize()
    config["options"]["port"] = str(value)
    update()

def launch():
    global config
    global proc
    if config is None:
        initialize()
    binpath = get_binary_path()
    if proc is None:
        print(f"launching FastEventServer: {binpath.name} {CONFIG_PATH}")
        proc = _sp.Popen([str(binpath), str(CONFIG_PATH)],
                         bufsize=1) # FIXME read the stderr from the app
        _time.sleep(0.5)

def read():
    if proc is not None:
        # FIXME: read the stderr from the app in case of any errors
        
        # try:
        #     _, err = proc.communicate()
        #     return err
        # except ValueError as e: # the process is shut down elsewhere
        #     return None
        return None
    else:
        raise RuntimeError("FastEventServer has not been launched")

def shutdown():
    global proc
    if config is None:
        initialize()
    if proc is not None:
        print("shutting down FastEventServer...")
        try:
            proc.wait(1)
            proc = None
        except:
            kill()

def kill():
    global proc
    if config is None:
        initialize()
    if proc is not None:
        code = proc.poll()
        if code is None:
            # still running
            print("***killing the FastEventServer process")
            proc.kill()
        else:
            print(f"the FastEventServer process exited with code {code}")
        proc = None

def load():
    if not CONFIG_PATH.exists():
        print(f"initializing FastEventServer config file at: {CONFIG_PATH}")
        return DEFAULT_CONFIG
    else:
        try:
            with open(CONFIG_PATH, "r") as src:
                return _json.load(src)
        except Exception as e:
            msg = f"{e}"
        raise RuntimeError(f"failed to read from '{CONFIG_PATH}', check the format: {e}")

def update():
    with open(CONFIG_PATH, "w") as out:
        _json.dump(config, out, indent=4)
    print(f"FastEventServer config: {config}")

import psutil
import os
import logging
import atexit
import signal
import sys

logging.getLogger().setLevel(logging.INFO)

from openbci.acquisition import Cyton
from openbci.stream.ws.server import run_websocket_server

pid = os.getegid()
logging.info(f"Running with ID: {pid}")

if os.path.exists('.process_id'):
    with open('.process_id', 'r') as file:
        oldpid = file.read()
        if oldpid.isdigit():
            oldpid = int(oldpid)
            try:
                os.kill(oldpid, signal.SIGKILL)
            except:
                pass

with open('.process_id', 'w') as file:
    file.write(str(pid))

config = {
    'ip_port': 8845,
    'user_dir': '.',

    # RFduino
    # 'module': 'CytonRFDuino',
    # 'sample_rate': Cyton.SAMPLE_RATE_250HZ,

    # WiFi
    'module': 'CythonWiFi',
    'ip_address': '192.168.1.185',
    'sample_rate': Cyton.SAMPLE_RATE_16KHZ,
}


@atexit.register
def goodbye():
    logging.info(f"Killing PID: {pid}")
    try:
        os.kill(pid, signal.SIGKILL)
        if os.path.exists('.process_id'):
            os.remove('.process_id')
        # if os.path.exists('.running'):
            # os.remove('.running')
    except:
        pass


# ----------------------------------------------------------------------
def run():
    """"""
    run_websocket_server(config)

# with open('.running', 'w') as file:
    # pass

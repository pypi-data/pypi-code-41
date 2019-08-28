"""PySide script to demo SideGears."""

import asyncio
import datetime
import logging
import os
import sys

import jsonrpcserver as rpc

from sidegears.kernel import RPCKernel, rpc_method

from PySide2 import QtCore, QtWidgets, QtWebEngineWidgets
from asyncqt import QEventLoop

@rpc_method
async def getcwd():
    return os.getcwd()

@rpc_method
async def logToKernel(message):
    print(message)
    return True

@rpc_method
async def multiply(x, y):
    """An example RPC method."""
    print('Received multiply method')
    return x*y

@rpc_method
async def scandir(path=None):
    """Return contents of directory"""
    if not path:
        path = os.getcwd()

    if not os.path.isdir(path):
        return dict(folders=[], files=[], status='Error - path is not a directory')

    folder_list = list()
    file_list = list()
    scan_iter = os.scandir(path)
    for entry in scan_iter:
        stat = entry.stat()
        dt = datetime.datetime.fromtimestamp(stat.st_mtime)
        modified = dt.strftime('%Y-%m-%d')
        size = stat.st_size
        #list_item = dict(name=entry.name, modified=modified, size=size)
        list_item = dict(name=entry.name, modified_sec=stat.st_mtime, size=size)
        if entry.is_dir():
            folder_list.append(list_item)
        elif entry.is_file():
            file_list.append(list_item)

    folder_list.sort(key=lambda x: x['name'])
    file_list.sort(key=lambda x: x['name'])
    return dict(folders=folder_list, files=file_list, status='OK')

# ------------------------------------------------
if __name__ == '__main__':
    app  = QtWidgets.QApplication(sys.argv)
    app.setApplicationDisplayName('SideGears/PySide Application')

    loop = QEventLoop(app)
    loop.set_debug(True)
    asyncio.set_event_loop(loop)

    # Start the kernel
    kernel = RPCKernel()
    # kernel.set_basic_logging(True)
    # kernel.set_debug(True)
    # kernel.set_trim_log_values(False)
    kernel.start()

    # Start browser
    view = QtWebEngineWidgets.QWebEngineView();
    view.setWindowTitle('SideGears/PySide Application')

    source_dir = os.path.abspath(os.path.dirname(__file__))
    client_path = os.path.join(source_dir, os.pardir, 'client', 'client.html')
    client_url = 'file://{}'.format(client_path)

    view.load(QtCore.QUrl(client_url));
    view.show();

    exit_code = app.exec_()

    # After browser has closed, stop the backend server
    with loop:
        loop.run_until_complete(kernel.stop())

    print('finis', exit_code)
    sys.exit(exit_code)

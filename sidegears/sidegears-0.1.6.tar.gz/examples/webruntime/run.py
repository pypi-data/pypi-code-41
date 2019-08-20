"""Example script to demo SideGears in browser."""

import datetime
import logging
import os
import sys

import webruntime

from sidegears.kernel import RPCKernel, rpc_method

rt = None

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
async def quit():
    print('Received quit message')
    rt.close()

@rpc_method
async def scandir(path=None):
    """"""
    if path is None:
        path = os.getcwd()

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
    return {'folders': folder_list, 'files': file_list}


# ------------------------------------------------
if __name__ == '__main__':
    kernel = RPCKernel()
    # kernel.set_basic_logging(True)
    # kernel.set_debug(True)
    # kernel.set_trim_log_values(False)
    kernel.start(close_on_disconnect=True)

    # Launch the web browser
    source_dir = os.path.abspath(os.path.dirname(__file__))
    client_path = os.path.join(source_dir, os.pardir, 'client', 'client.html')
    url = 'file://{}'.format(client_path)
    rt = webruntime.launch(url, runtime='app', title='SideGears')
    print('Using web runtime: {}'.format(rt.get_name()))

    # Block until kernel closes (when websocket disconnects)
    kernel.wait_until_closed()

    print('finis')

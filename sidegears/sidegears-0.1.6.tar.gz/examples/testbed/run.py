"""PySide script to demo SideGears."""

import asyncio
import datetime
import logging
import os
import sys

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
    kernel = RPCKernel()
    kernel.set_basic_logging(True)
    kernel.set_debug(True)
    kernel.set_trim_log_values(False)

    kernel.start(close_on_disconnect=False)
    print('The kernel is now running.')
    print('Open a browser to the examples/client.html to test/debug.')
    print('Exit this script using Control-C')
    print()

    # Block until kernel closes (when websocket disconnects)
    kernel.wait_until_closed()

    print('finis')

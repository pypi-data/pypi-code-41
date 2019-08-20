"""
Sample script showing how to do remote port forwarding over paramiko.
This script connects to the requested SSH server and sets up remote port
forwarding (the openssh -R option) from a remote port through a tunneled
connection to a destination reachable from the local machine.
"""

import sshtunnel
from kernel_gateway import launch_instance
import getpass
import os
import socket
import select
import sys
import time
import threading
from optparse import OptionParser

import paramiko
import logging

logging.basicConfig()
logging.getLogger("paramiko").setLevel(logging.DEBUG)

SSH_PORT = 22
DEFAULT_PORT = 4000

def handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print("Forwarding request to %s:%d failed: %r" % (host, port, e))
        return

    print(
        "Connected!  Tunnel open %r -> %r -> %r"
        % (chan.origin_addr, chan.getpeername(), (host, port))
    )
    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
    chan.close()
    sock.close()
    print("Tunnel closed from %r" % (chan.origin_addr,))


def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("localhost", server_port)
    channel = transport.open_session()
    channel.get_pty()
    channel.invoke_shell()
    print("Connected", channel.recv(1024))
    print("Launched instance")
    while True:
        chan = transport.accept(1000)
        print("RFT", chan, channel)
        if chan is None:
            continue
        thr = threading.Thread(
            target=handler, args=(chan, remote_host, remote_port)
        )
        thr.setDaemon(True)
        thr.start()


client = paramiko.SSHClient()
transport=paramiko.Transport(('serveo.net', 22))
transport.connect()
transport.auth_interactive_dumb("vanpelt")
transport.use_compression(True)
transport.set_keepalive(60)
print("Connected")
reverse_forward_tunnel(80, "localhost", 8889, transport)

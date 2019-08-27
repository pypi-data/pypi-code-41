import json
import os
import sys
import socket
import errno
import time
import traceback


def eprint(*args, debug=False, fatal=False):
    print(*args, file=sys.stderr)
    if debug:
        traceback.print_exc(file=sys.stderr)
    if fatal:
        sys.exit(1)


def expired(exp):
    return time.time() > exp


def is_file_accessible(path, mode='r'):
    file_exists = os.path.exists(path) and os.path.isfile(path)
    if not file_exists:
        return False

    """
    Check if the file or directory at `path` can
    be accessed by the program using `mode` open flags.
    """
    try:
        f = open(path, mode)
        f.close()
    except IOError:
        return False
    return True


def is_port_accessible(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((host, port))
    except socket.error as e:
        return e.errno != errno.EADDRINUSE
    s.close()
    return True


def silent_file_remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def to_json(body):
    try:
        return json.loads(body.text)
    except Exception as ex:
        raise ex

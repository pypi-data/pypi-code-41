import contextlib
import os
import sys
import shutil
import stat
import subprocess
import platform
import re

import errno

from aos.constant import *


# Directory navigation
@contextlib.contextmanager
def cd(newdir):
    prevdir = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(prevdir)


def relpath(root, path):
    return path[len(root) + 1:]


def staticclass(cls):
    for k, v in cls.__dict__.items():
        if hasattr(v, '__call__') and not k.startswith('__'):
            setattr(cls, k, staticmethod(v))

    return cls


# Logging and output
def log(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def message(msg):
    return "[AliOS-Things] %s\n" % msg


def info(msg, level=1):
    if level <= 0 or verbose:
        for line in msg.splitlines():
            log(message(line))


def action(msg):
    for line in msg.splitlines():
        log(message(line))


def warning(msg):
    for line in msg.splitlines():
        sys.stderr.write("[AliOS-Things] WARNING: %s\n" % line)
    sys.stderr.write("---\n")


def error(msg, code=-1):
    for line in msg.splitlines():
        sys.stderr.write("[AliOS-Things] ERROR: %s\n" % line)
    sys.stderr.write("---\n")
    sys.exit(code)


def progress_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


progress_spinner = progress_cursor()


def progress():
    sys.stdout.write(progress_spinner.next())
    sys.stdout.flush()
    sys.stdout.write('\b')


# Process execution
class ProcessException(Exception):
    pass


def rmtree_readonly(directory):
    def remove_readonly(func, path, _):
        os.chmod(path, stat.S_IWRITE)
        func(path)

    shutil.rmtree(directory, onerror=remove_readonly)


def popen(command, suppress_error=None, stdin=None, **kwargs):
    # print for debugging
    info('Exec "' + ' '.join(command) + '" in ' + os.getcwd())

    # fix error strings
    try:
        command_line = command.split()
    except:
        command_line = command

    try:
        proc = subprocess.Popen(command, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (
                command_line[0], command_line[0]), e[0])
        else:
            raise e

    if proc.wait() != 0:
        if not suppress_error:
            raise ProcessException(proc.returncode, command_line[0], ' '.join(command_line), os.getcwd())

    return proc.returncode


def pquery(command, stdin=None, **kwargs):
    if very_verbose:
        info('Query "' + ' '.join(command) + '" in ' + os.getcwd())
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (
                command[0], command[0]), e[0])
        else:
            raise e

    stdout, _ = proc.communicate(stdin)

    if very_verbose:
        log(str(stdout).strip() + "\n")

    if proc.returncode != 0:
        raise ProcessException(proc.returncode, command[0], ' '.join(command), os.getcwd())

    return stdout

def exec_cmd(command, suppress_error=None, stdin=None, **kwargs):
    """ Run command and return output, errcode """
    info('Exec "' + ' '.join(command) + '" in ' + os.getcwd())

    # fix error strings
    if isinstance(command, str):
        command_line = command.split()
    else:
        command_line = command

    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except OSError as e:
        if e[0] == errno.ENOENT:
            error(
                "Could not execute \"%s\".\n"
                "Please verify that it's installed and accessible from your current path by executing \"%s\".\n" % (
                command_line[0], command_line[0]), e[0])
        else:
            raise e

    output, err = proc.communicate()
    if proc.wait() != 0:
        if not suppress_error:
            raise ProcessException(proc.returncode, command_line[0], ' '.join(command_line), os.getcwd())

    return output, err

def get_country_code():
    import requests
    import json
    url = "https://geoip-db.com/json"
    try:
        res = requests.get(url, timeout = 5)
        data = json.loads(res.text)
        return data['country_code']
    except Exception:
        return 'CN'

def is_domestic():
    if get_country_code() == 'CN':
        return True
    else:
        return False

def get_host_os():
    host_os = platform.system()
    if host_os == 'Windows':
        host_os = 'Win32'
    elif host_os == 'Linux':
        if platform.machine().endswith('64'):
            bit = '64'
        else:
            bit = '32'
        host_os += bit
    elif host_os == 'Darwin':
        host_os = 'OSX'
    else:
        host_os = None
    return host_os

def get_aos_url():
    """Figure out proper URL for downloading AliOS-Things."""
    if is_domestic():
        aos_url = 'https://gitee.com/alios-things/AliOS-Things.git'
    else:
        aos_url = 'https://github.com/alibaba/AliOS-Things.git'

    return aos_url

def cd_aos_root():
    original_dir = os.getcwd()
    host_os = get_host_os()
    if host_os == 'Win32':
        sys_root = re.compile(r'^[A-Z]{1}:\\$')
    else:
        sys_root = re.compile('^/$')
    while os.path.isdir('./include/aos') == False and os.path.isdir('./kernel/rhino') == False:
        os.chdir('../')
        if sys_root.match(os.getcwd()):
            return 'fail', original_dir
    return 'success', original_dir

def get_aos_project():
    """ Figure out the aos project dir """
    curr_dir = os.getcwd()

    host_os = get_host_os()
    if host_os == 'Win32':
        sys_root = re.compile(r'^[A-Z]{1}:\\$')
    else:
        sys_root = re.compile('^/$')

    while not os.path.isfile(os.path.join(curr_dir, ".aos", OS_CONFIG)):
        curr_dir = os.path.abspath(os.path.join(curr_dir, "../"))

        if sys_root.match(curr_dir):
            return None

    return curr_dir

def which(program):
    if platform.system() == 'Windows' and program.endswith('.exe') == False:
        program += '.exe'

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def cmd_version_match(cmd, version):
    cmd = which(cmd)
    if cmd == None:
        return False
    if version == 'all':
        return True
    match = False
    try:
        ret = subprocess.check_output([cmd, '-v'], stderr=subprocess.STDOUT)
    except:
        return match
    lines = ret.split('\n')
    for line in lines:
        if version in line:
            match = True
            break;
    return match

def get_config_value(keyword, config_file=None):
    """ Get value of keyword from config file """
    value = None
    if not config_file:
        config_file = '.config'

    if not os.path.isfile(config_file):
        return value

    with open(config_file) as f:
        for line in f.readlines():
            match = re.match(r'^([\w+-]+)\=(.*)$', line)
            if match and match.group(1) == keyword:
                value = match.group(2).replace('"','')

    return value

def get_board_dir(board):
    """ Get board dir that include version number """
    board_dir = None
    for root, dirs, files in os.walk('./board/'):
        for tmpdir in dirs:
            if "%s-" % board in tmpdir:
                board_dir = tmpdir

    return board_dir

def update_config_in():
    """ Call build/scripts/gen_configin.py """
    ret = 0
    gen_config_script = "build/scripts/gen_configin.py"
    if os.path.isfile(gen_config_script):
        ret = popen(gen_config_script)

    return ret

def check_url(url):
    """ Check if the url available """
    ret = 0
    code = 404

    try:
        from urllib2 import urlopen
    except:
        from urllib.request import urlopen

    try:
        resp = urlopen(url)
        code = resp.getcode()
    except:
        pass

    if code != 200:
        ret = 1

    return ret

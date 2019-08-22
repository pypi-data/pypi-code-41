import os
import sys
import imp
import gzip
import argparse
import datetime
import random
import string


def generate_uid(n=4):
    random_str = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(n))
    random_str = '%s_%s' % (
        datetime.datetime.now().strftime("%y%m%d%H%M%S.%f"), random_str)
    return random_str


def package_modules(package):
    pathname = package.__path__[0]
    return set(['.'.join([package.__name__, os.path.splitext(module)[0]])
                for module in os.listdir(pathname)
                if module.endswith('.py')
                and not module.startswith('__init__')])


def package_files(package, extension):
    pathname = package.__path__[0]
    return set([os.path.abspath(os.path.join(pathname, file))
                for file in os.listdir(pathname)
                if file.endswith(extension)])


def try_import(path, module_name):
    try:
        mod = imp.load_module(module_name, None,
                              os.path.join(path, module_name),
                              ('', '', 5))
    except ImportError:
        init_path = os.path.join(path, module_name, '__init__.py')
        try:
            with open(init_path, 'a'):
                os.utime(init_path, None)
            mod = imp.load_module(module_name, None,
                                  os.pathh.join(path, module_name),
                                  ('', '', 5))
        except IOError:
            raise Exception(('There is no directory in the path %s. '
                             'Check your configuration or create '
                             'the directory in the desired path.') %
                            os.path.join(path, module_name))
    return mod


def get_modules(parent, subparsers, progs):
    mods = package_modules(parent)
    for mod in sorted(mods):
        try:
            __import__(mod)
            mod_name = mod.split('.')[-1]
            m = getattr(parent, mod_name)
            m.add_parser(subparsers, mod_name)
            progs[mod_name] = getattr(m, mod_name)
        except AttributeError:
            pass
    return progs


def get_modules_names(parent):
    mods = package_modules(parent)
    modules = []
    for mod in mods:
        try:
            __import__(mod)
            mod_name = mod.split('.')[-1]
            modules.append(mod_name)
        except AttributeError:
            pass
    return modules


def get_module_method(parent, module, method):
    mods = package_modules(parent)
    for mod in mods:
        try:
            __import__(mod)
            mod_name = mod.split('.')[-1]
            if mod_name == module:
                m = getattr(parent, mod_name)
                return getattr(m, method)
        except AttributeError:
            pass


def xopen(filename, mode='r'):
    '''
    Replacement for the "open" function that can also open
    files that have been compressed with gzip. If the filename ends with .gz,
    the file is opened with gzip.open(). If it doesn't, the regular open()
    is used. If the filename is '-', standard output (mode 'w') or input
    (mode 'r') is returned.
    '''
    assert isinstance(filename, str)
    if filename == '-':
        return sys.stdin if 'r' in mode else sys.stdout
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    else:
        return open(filename, mode)


def check_exit_code(process, sting, results_dict, log):
    log.log.info('Checking exit code for process %s' % string)
    code = process.returncode
    info = 'Process terminated, exit code: %s' % code
    if code == 0:
        log.log.info(info)
    else:
        log.log.error(info)
        log.log.warning('Removing results:')
        for result in results_dict:
            for res in results_dict[result]:
                try:
                    log.log.warning('Attempt to remove results: %s' % res)
                    os.remove(res)
                except OSError as e:
                    log.log.warning('Failed to remove results: %s; %s'
                                    % (res, e))
        log.log.warning('Terminate the process')
        raise Exception('Process %s exited with code %s' % (string, code))


def human_format(num, base=1000):
    prefix_index = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    magnitude = 0
    orig = num
    dec = 0
    while abs(num) >= base:
        magnitude += 1
        num /= float(base)
    try:
        dec = str(num).split('.')[1]
        dec = float('0.%s' % dec) * base**magnitude
        dec = human_format(int(dec))
        if dec == '0':
            dec = ''
    except IndexError:
        dec = ''
    try:
        return '%i%s%s' % (num, prefix_index[magnitude], dec)
    except IndexError:
        return '%i' % orig


def bases_format(string, base=1000):
    symbols = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
    symbolsB = ['%sB' % x for x in symbols]
    num = ''
    while string and string[0:1].isdigit() or string[0:1] == '.':
        num += string[0]
        string = string[1:]
    letter = string.strip().upper()
    assert num.isdigit() and letter in symbols + symbolsB
    num = float(num)
    if len(letter) <= 1 and letter != "B":
        prefix = {symbols[0]: 1}
        for i, string in enumerate(symbols[1:]):
            prefix[string] = base**(i + 1)
    else:
        prefix = {symbolsB[0]: 1}
        for i, string in enumerate(symbolsB[1:]):
            prefix[string] = base**(i + 1)
    return int(num * prefix[letter])


class Tee(object):

    def __init__(self, f1, f2):
        self.f1, self.f2 = f1, f2

    def write(self, msg):
        self.f1.write(msg)
        self.f2.write(msg)


class SubcommandHelpFormatter(argparse.RawDescriptionHelpFormatter):

    def _format_action(self, action):
        parts = super(argparse.RawDescriptionHelpFormatter,
                      self)._format_action(action)
        if action.nargs == argparse.PARSER:
            parts = "\n".join(parts.split("\n")[1:])
        return parts


class DefaultHelpParser(argparse.ArgumentParser):

    def error(self, message):
        import sys
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

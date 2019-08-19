# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE in the project root
# for license information.

from __future__ import absolute_import, print_function, unicode_literals

import os.path
import runpy
import sys

# ptvsd.__main__ should have preloaded pydevd properly before importing this module.
# Otherwise, some stdlib modules above might have had imported threading before pydevd
# could perform the necessary detours in it.
assert "pydevd" in sys.modules
import pydevd

import ptvsd
from ptvsd.common import compat, fmt, log, options as common_opts
from ptvsd.server import multiproc, options


TARGET = "<filename> | -m <module> | -c <code> | --pid <pid>"

HELP = """ptvsd {0}
See https://aka.ms/ptvsd for documentation.

Usage: ptvsd [--client] --host <address> [--port <port>]
             [--wait]
             [--multiprocess]
             [--log-dir <path>] [--log-stderr]
             {1}
""".format(
    ptvsd.__version__, TARGET
)


def in_range(parser, start, stop):
    def parse(s):
        n = parser(s)
        if start is not None and n < start:
            raise ValueError(fmt("must be >= {0}", start))
        if stop is not None and n >= stop:
            raise ValueError(fmt("must be < {0}", stop))
        return n

    return parse


port = in_range(int, 0, 2 ** 16)

pid = in_range(int, 0, None)


def print_help_and_exit(switch, it):
    print(HELP, file=sys.stderr)
    sys.exit(0)


def print_version_and_exit(switch, it):
    print(ptvsd.__version__)
    sys.exit(0)


def set_arg(varname, parser=(lambda x: x), options=options):
    def action(arg, it):
        value = parser(next(it))
        setattr(options, varname, value)

    return action


def set_true(varname, options=options):
    def do(arg, it):
        setattr(options, varname, True)

    return do


def set_log_stderr():
    def do(arg, it):
        log.stderr_levels |= set(log.LEVELS)

    return do


def set_target(kind, parser=(lambda x: x), positional=False):
    def do(arg, it):
        options.target_kind = kind
        options.target = parser(arg if positional else next(it))

    return do


# fmt: off
switches = [
    # Switch                    Placeholder         Action                                      Required
    # ======                    ===========         ======                                      ========

    # Switches that are documented for use by end users.
    (('-?', '-h', '--help'),    None,               print_help_and_exit,                        False),
    (('-V', '--version'),       None,               print_version_and_exit,                     False),
    ('--client',                None,               set_true('client'),                         False),
    ('--host',                  '<address>',        set_arg('host'),                            True),
    ('--port',                  '<port>',           set_arg('port', port),                      False),
    ('--wait',                  None,               set_true('wait'),                           False),
    ('--multiprocess',          None,               set_true('multiprocess'),                   False),
    ('--log-dir',               '<path>',           set_arg('log_dir', options=common_opts),    False),
    ('--log-stderr',            None,               set_log_stderr(),                           False),

    # Switches that are used internally by the IDE or ptvsd itself.
    ('--subprocess-of',         '<pid>',            set_arg('subprocess_of', pid),              False),
    ('--subprocess-notify',     '<port>',           set_arg('subprocess_notify', port),         False),

    # Targets. The '' entry corresponds to positional command line arguments,
    # i.e. the ones not preceded by any switch name.
    ('',                        '<filename>',       set_target('file', positional=True),        False),
    ('-m',                      '<module>',         set_target('module'),                       False),
    ('-c',                      '<code>',           set_target('code'),                         False),
    ('--pid',                   '<pid>',            set_target('pid', pid),                     False),
]
# fmt: on


def parse(args):
    seen = set()
    it = (compat.filename(arg) for arg in args)

    while True:
        try:
            arg = next(it)
        except StopIteration:
            raise ValueError("missing target: " + TARGET)

        switch = arg if arg.startswith("-") else ""
        for i, (sw, placeholder, action, _) in enumerate(switches):
            if not isinstance(sw, tuple):
                sw = (sw,)
            if switch in sw:
                break
        else:
            raise ValueError("unrecognized switch " + switch)

        if i in seen:
            raise ValueError("duplicate switch " + switch)
        else:
            seen.add(i)

        try:
            action(arg, it)
        except StopIteration:
            assert placeholder is not None
            raise ValueError(fmt("{0}: missing {1}", switch, placeholder))
        except Exception as exc:
            raise ValueError(fmt("invalid {0} {1}: {2}", switch, placeholder, exc))

        if options.target is not None:
            break

    for i, (sw, placeholder, _, required) in enumerate(switches):
        if not required or i in seen:
            continue
        if isinstance(sw, tuple):
            sw = sw[0]
        message = fmt("missing required {0}", sw)
        if placeholder is not None:
            message += " " + placeholder
        raise ValueError(message)

    if options.target_kind == "pid" and options.wait:
        raise ValueError("--pid does not support --wait")

    return it


def setup_connection():
    pydevd.apply_debugger_options(
        {
            "server": not options.client,
            "client": options.host,
            "port": options.port,
            "multiprocess": options.multiprocess,
        }
    )

    if options.multiprocess:
        multiproc.listen_for_subprocesses()

    # We need to set up sys.argv[0] before invoking attach() or enable_attach(),
    # because they use it to report the 'process' event. Thus, we can't rely on
    # run_path() and run_module() doing that, even though they will eventually.

    if options.target_kind == "code":
        sys.argv[0] = "-c"
    elif options.target_kind == "file":
        sys.argv[0] = options.target
    elif options.target_kind == "module":
        # Add current directory to path, like Python itself does for -m. This must
        # be in place before trying to use find_spec below to resolve submodules.
        sys.path.insert(0, "")

        # We want to do the same thing that run_module() would do here, without
        # actually invoking it. On Python 3, it's exposed as a public API, but
        # on Python 2, we have to invoke a private function in runpy for this.
        # Either way, if it fails to resolve for any reason, just leave argv as is.
        try:
            if sys.version_info >= (3,):
                from importlib.util import find_spec

                spec = find_spec(options.target)
                if spec is not None:
                    sys.argv[0] = spec.origin
            else:
                _, _, _, sys.argv[0] = runpy._get_module_details(options.target)
        except Exception:
            log.exception("Error determining module path for sys.argv")
    else:
        assert False
    log.debug("sys.argv after patching: {0!r}", sys.argv)

    addr = (options.host, options.port)
    if options.client:
        ptvsd.attach(addr)
    else:
        ptvsd.enable_attach(addr)

    if options.wait:
        ptvsd.wait_for_attach()


def run_file():
    setup_connection()

    # run_path has one difference with invoking Python from command-line:
    # if the target is a file (rather than a directory), it does not add its
    # parent directory to sys.path. Thus, importing other modules from the
    # same directory is broken unless sys.path is patched here.
    if os.path.isfile(options.target):
        dir = os.path.dirname(options.target)
        sys.path.insert(0, dir)
    else:
        log.debug("Not a file: {0!j}", options.target)

    log.describe_environment("Pre-launch environment:")
    log.info("Running file {0!j}", options.target)
    runpy.run_path(options.target, run_name="__main__")


def run_module():
    setup_connection()

    # On Python 2, module name must be a non-Unicode string, because it ends up
    # a part of module's __package__, and Python will refuse to run the module
    # if __package__ is Unicode.
    target = (
        compat.filename_bytes(options.target)
        if sys.version_info < (3,)
        else options.target
    )

    log.describe_environment("Pre-launch environment:")
    log.info("Running module {0!r}", target)

    # Docs say that runpy.run_module is equivalent to -m, but it's not actually
    # the case for packages - -m sets __name__ to '__main__', but run_module sets
    # it to `pkg.__main__`. This breaks everything that uses the standard pattern
    # __name__ == '__main__' to detect being run as a CLI app. On the other hand,
    # runpy._run_module_as_main is a private function that actually implements -m.
    try:
        run_module_as_main = runpy._run_module_as_main
    except AttributeError:
        log.warning("runpy._run_module_as_main is missing, falling back to run_module.")
        runpy.run_module(target, alter_sys=True)
    else:
        run_module_as_main(target, alter_argv=True)


def run_code():
    log.describe_environment("Pre-launch environment:")
    log.info("Running code:\n\n{0}", options.target)

    # Add current directory to path, like Python itself does for -c.
    sys.path.insert(0, "")
    code = compile(options.target, "<string>", "exec")
    setup_connection()
    eval(code, {})


def attach_to_pid():
    def quoted_str(s):
        if s is None:
            return s
        assert not isinstance(s, bytes)
        unescaped = set(chr(ch) for ch in range(32, 127)) - {'"', "'", "\\"}

        def escape(ch):
            return ch if ch in unescaped else "\\u%04X" % ord(ch)

        return 'u"' + "".join(map(escape, s)) + '"'

    log.info("Attaching to process with ID {0}", options.target)

    pid = options.target
    host = quoted_str(options.host)
    port = options.port
    client = options.client
    log_dir = quoted_str(ptvsd.common.options.log_dir)

    ptvsd_path = os.path.abspath(os.path.join(ptvsd.server.__file__, "../.."))
    if isinstance(ptvsd_path, bytes):
        ptvsd_path = ptvsd_path.decode(sys.getfilesystemencoding())
    ptvsd_path = quoted_str(ptvsd_path)

    # pydevd requires injected code to not contain any single quotes.
    code = """
import os
assert os.getpid() == {pid}

import sys
sys.path.insert(0, {ptvsd_path})
import ptvsd
from ptvsd.common import log, options
del sys.path[0]

options.log_dir = {log_dir}
log.to_file()
log.info("Bootstrapping injected debugger.")

if {client}:
    ptvsd.attach(({host}, {port}))
else:
    ptvsd.enable_attach(({host}, {port}))
""".format(
        **locals()
    )

    log.debug('Injecting debugger into target process: \n"""{0}\n"""'.format(code))
    assert "'" not in code, "Injected code should not contain any single quotes"

    pydevd_attach_to_process_path = os.path.join(
        os.path.dirname(pydevd.__file__), "pydevd_attach_to_process"
    )
    sys.path.insert(0, pydevd_attach_to_process_path)
    from add_code_to_python_process import run_python_code

    run_python_code(pid, code, connect_debugger_tracing=True)


def main():
    original_argv = sys.argv
    try:
        sys.argv[1:] = parse(sys.argv[1:])
    except Exception as ex:
        print(HELP + "\nError: " + str(ex), file=sys.stderr)
        sys.exit(2)

    log.to_file()
    log.describe_environment("ptvsd.server startup environment:")
    log.info(
        "sys.argv before parsing: {0!r}\n" "         after parsing:  {1!r}",
        original_argv,
        sys.argv,
    )

    try:
        run = {
            "file": run_file,
            "module": run_module,
            "code": run_code,
            "pid": attach_to_pid,
        }[options.target_kind]
        run()
    except SystemExit as ex:
        log.exception("Debuggee exited via SystemExit: {0!r}", ex.code, level="debug")
        raise

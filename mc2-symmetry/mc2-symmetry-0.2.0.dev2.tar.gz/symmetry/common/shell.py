import cmd
import os
import shlex
import time
from collections import OrderedDict
from inspect import Parameter, signature, Signature
from typing import List


class ArgumentError(Exception):
    pass


def convert_args(args: List, sig: Signature):
    i = 0
    result = OrderedDict()

    if len(args) > len(sig.parameters):
        raise ArgumentError('Too many arguments: takes %d but %d were given' % (len(sig.parameters), len(args)))

    for param in sig.parameters.values():

        if i >= len(args):
            if param.default == Parameter.empty:
                raise ArgumentError('Missing argument %d' % i)

            val = param.default
        else:
            val = args[i]

        tpe = param.annotation

        if tpe != Parameter.empty and tpe:
            try:
                val = tpe(val)
            except ValueError as e:
                raise ArgumentError('Could not convert argument %d to %s (%s)' % (i, tpe.__name__, e))

        result[param.name] = val

        i += 1

    return result


def create_doc(fn):
    name = fn.__name__.lstrip('do_')
    sig = signature(fn)

    doc = ['']

    params = []
    for pname, param in sig.parameters.items():
        if pname == 'self':
            continue

        if param.default != Parameter.empty:
            params.append('[%s]' % pname)
        else:
            params.append(pname)

    doc.append('Usage: %s %s' % (name, ' '.join(params)))

    if fn.__doc__:

        lines = fn.__doc__.splitlines()
        lines = [line.strip() for line in lines]
        docs = [line for line in lines if not line.startswith(':param')]
        if not docs[-1]:
            del docs[-1]

        parameters = [line[6:].strip() for line in lines if line.startswith(':param')]

        for line in docs:
            line = line.strip()
            doc.append('  ' + line)

        doc.append('parameters:')
        # TODO: make parameter dict and get information from signature
        for param in parameters:
            doc.append('  ' + param)

        doc.append('')

    return os.linesep.join(doc)


def parsed(fn):
    """
    Function decorator that allows the function to be called with the function arguments encoded as a string.
    :param fn:
    :return:
    """

    def wrapper(shell: cmd.Cmd, line: str):
        try:
            args = [shell] + shlex.split(line)
            kwargs = convert_args(args, signature(fn))
            return fn(**kwargs)
        except ArgumentError as e:
            if isinstance(shell, Shell):
                shell.on_argument_error(e)
            else:
                raise e

    wrapper.__doc__ = create_doc(fn)

    return wrapper


def print_tabular(data, columns=None, widths=None, printer=None):
    if not data and not columns:
        return

    printer = printer or print
    columns = columns or data[0].keys()
    if not widths:
        widths = list()
        for c in columns:
            max_len = len(c)

            for row in data:
                max_len = max(max_len, len(str(row[c])))

            widths.append(-max_len)

    sep = ['-' * abs(i) for i in widths]
    sep = '+-' + '-+-'.join(sep) + '-+'

    row_fmt = ['%%%ds' % widths[i] for i in range(len(widths))]
    row_fmt = '| ' + ' | '.join(row_fmt) + ' |'

    header = tuple(columns)

    printer(sep)
    printer(row_fmt % header)
    printer(sep)

    for record in data:
        row = tuple([record[k] for k in columns])
        printer(row_fmt % row)

    printer(sep)


class Shell(cmd.Cmd):

    def run(self):
        if not self.istty():
            self.prompt = ''
            self.intro = None

        try:
            self.cmdloop()
        except KeyboardInterrupt:
            self.postloop()
            return

    def istty(self):
        return os.isatty(0)

    def on_argument_error(self, error: ArgumentError):
        self.println('argument error:', str(error))

    def println(self, *messages):
        message = ' '.join([str(msg) for msg in messages])
        self.stdout.write(message)
        self.stdout.write(os.linesep)
        self.stdout.flush()

    def precmd(self, line):
        if line.startswith('#'):
            return ''

        return super().precmd(line)

    def emptyline(self):
        pass

    def default(self, line):
        if line == 'EOF':
            if self.istty():
                self.stdout.write('\n')
            else:
                return self.do_exit(line)
        else:
            super().default(line)

    @parsed
    def do_date(self):
        self.println(time.time())

    @parsed
    def do_source(self, source: str):
        if not os.path.isfile(source):
            raise ArgumentError('No such file: %s' % source)

        with open(source, 'r') as fd:
            lines = fd.readlines()

        self.cmdqueue.extend(lines)

    def do_echo(self, msg):
        self.println(*shlex.split(msg))

    @parsed
    def do_sleep(self, sec: float):
        """
        Delay execution for a given number of seconds.  The argument may be a floating point number for subsecond
        precision.

        :param sec: number of seconds
        """
        time.sleep(sec)

    def do_exit(self, _):
        return True

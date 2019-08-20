"""MORE IPython ``%magic`` functions."""

import os
import sys
from inspect import getsourcefile, getsourcelines

import zetup
from moreshell import IPython_magic, IPython_magic_module, with_arguments
from moretools import getfunc
from path import Path
from six import reraise
from zetup import call

IPython_magic_module(__name__, ['dev'])


@IPython_magic(
    with_arguments
    ('object')
    ('-e', '--editor')
    ('-f', '--format')
)
def dev(shell, args):
    """
    Open the file containing the code for the given object.

    And jump to the location of its definition

    By taking the command from the ``--editor`` option or from the ``EDITOR``
    environment variable, and running it with an argument created from the
    format string ``{file}:{line}``, which can be customized using the
    ``--format`` option

    The subprocess is started with ``shell=True``

    If no line number can be determined for the given ``object``, then the
    format string is ignored, and only the file path is used
    """
    editor = args.editor or os.environ.get('EDITOR')
    if not editor:
        raise RuntimeError("No EDITOR environment variable defined")

    editor_arg_format = args.format or "{file}:{line}"
    obj = eval(args.object, shell.user_ns)

    exceptions = []
    try:
        filename = getsourcefile(obj)
    except TypeError as exc:
        exceptions.append(exc)

        obj = type(obj)
        try:
            filename = getsourcefile(obj)
        except TypeError as exc:
            exceptions.append(exc)

            def getfile(base):
                try:
                    return getsourcefile(base)

                except TypeError as exc:
                    exceptions.append(exc)
                    return None

            for obj in obj.mro()[1:]:
                filename = getfile(obj)
                if filename is not None:
                    break

            else:
                raise TypeError(
                    "Can't find any source file for given object, its "
                    "class, or base classes: {!r}"
                    .format(exceptions))

    try:
        lineno = getsourcelines(obj)[1]
    except TypeError:
        lineno = 0

    editor_arg = Path(filename).realpath()
    if lineno:
        editor_arg = editor_arg_format.format(file=editor_arg, line=lineno)
    return call('{} "{}"'.format(editor, editor_arg), shell=True)

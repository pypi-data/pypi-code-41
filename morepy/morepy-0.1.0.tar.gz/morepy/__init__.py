import zetup
from moreshell import load_magic_modules

zetup.toplevel(__name__, ['load'])


def load(shell):
    """
    Load all IPython ``%magic`` functions from :mod:`morepy.magic`.

    :param shell:
        The ``IPython`` shell instance
    """
    load_magic_modules('magic', package=__name__, shell=shell)


def load_ipython_extension(shell):
    """Call on running ``%load_ext morepy`` from the IPython `shell`."""
    load(shell)

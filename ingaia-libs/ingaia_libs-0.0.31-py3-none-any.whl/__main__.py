"""------------------------------
inGaia python utility library
------------------------------
Version: {__version__}
"""

from ingaia import __version__


def main(*args, **kwargs):
    print(__doc__.replace('{__version__}', __version__))


if __name__ == "__main__":
    main()

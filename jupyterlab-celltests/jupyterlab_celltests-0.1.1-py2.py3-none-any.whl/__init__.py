from ._version import __version__  # noqa: F401


def _jupyter_server_extension_paths():
    return [{
        "module": "jupyterlab_celltests.extension"
    }]

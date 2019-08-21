from pathlib import Path

from ..Task import Task
from ..utils import render


class TarTask(Task):
    """
    A task to run tar command.

    .. seealso:: Task()
    """

    default_cmd = "tar"

    def _run(self):
        """
        Create a TAR archive using user settings.
        """
        cp_ext = {".gz": "gzip", ".bz2": "bzip2", ".xz": "xz"}
        cp_args = {"gzip": "-z", "bzip2": "-j", "xz": "-J"}
        repo = Path(self._config.get("repo"))
        archive = repo / render(self._config.get("name", "{hostname}-{date}.tar.gz"))
        compression = self._config.get("compression", None)
        if compression is None:
            compression = cp_ext[archive.suffix]
        cp_arg = cp_args[compression]
        tar_cmds = [self._cmd, "-c", cp_arg, "-f", str(archive)]
        tar_cmds.extend(set(self._config.get("directories", [])))
        self._exec(tar_cmds)

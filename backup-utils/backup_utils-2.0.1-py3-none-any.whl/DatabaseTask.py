from pathlib import Path
from importlib import import_module
from .Task import Task


class DatabaseTask(Task):
    """
    Parent DatabaseTask class, if you create a DatabaseTask,
    your class must be a child of this class.
    This class is a child of `Task`.

    .. seealso:: Task()
    """

    def __init__(self, *args, **kwargs):
        """
        Test if the directory to backup database file exists.

        .. seealso:: Task.__init__()
        """
        super().__init__(*args, **kwargs)
        self._bak_dir = (
            Path(self._config.get("backup_directory", "")).expanduser().resolve()
        )
        if not self._bak_dir.exists():
            raise ValueError("'{}' directory don't exists !".format(self._bak_dir))

    @property
    def backup_dir(self):
        """
        Return the directory containing database backup.

        :return: Directory containing database backup.
        :rtype: str
        """
        return str(self._bak_dir)

    def compress(self, data=b"", fname="dump.sql"):
        cp_ext = {
            "gzip": (".gz", "gzip"),
            "bzip2": (".bz2", "bz2"),
            "xz": (".xz", "lzma"),
        }
        compression = self._config.get("compression", None)
        if compression is None or compression not in cp_ext:
            with open(fname, "wb") as f:
                f.write(data)
        else:
            ext, cp_name = cp_ext[compression]
            cp_mod = import_module(cp_name)
            with open(fname + ext, "wb") as f:
                f.write(cp_mod.compress(data))

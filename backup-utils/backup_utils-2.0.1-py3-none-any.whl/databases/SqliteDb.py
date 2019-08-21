from pathlib import Path
from datetime import date

from ..DatabaseTask import DatabaseTask


class SqliteDb(DatabaseTask):
    """
    Sqlite driver for DatabaseTask.
    """

    default_cmd = "sqlite3"

    def _run(self):
        """
        Create a backup of a database in mysql using mysqldump
        """
        now = str(date.today())
        for db in self._config.get("database", []):
            db_file = Path(db).expanduser().resolve()
            if not db_file.exists():
                raise ValueError("'{}' file don't exist !".format(db_file))
            cmds = [self._cmd, str(db_file), ".dump"]
            proc = self._exec(cmds)
            bak_name = "{database}-{date}.sql".format(database=db_file.stem, date=now)
            self.compress(data=proc.stdout, fname=str(Path(self.backup_dir) / bak_name))

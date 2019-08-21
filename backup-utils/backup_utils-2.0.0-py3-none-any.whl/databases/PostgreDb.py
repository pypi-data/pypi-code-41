from pathlib import Path
from datetime import date
from os import environ

from ..DatabaseTask import DatabaseTask


class PostgreDb(DatabaseTask):
    """
    Postgre driver for DatabaseTask.
    """

    default_cmd = "pg_dump"

    def _run(self):
        """
        Create a backup of a database in mysql using mysqldump
        """
        now = str(date.today())
        for db in self._config.get("database", []):
            uri_args = {
                "user": db.get("user"),
                "pswd": db.get("pswd"),
                "host": db.get("host", "localhost"),
                "port": db.get("port", 5432),
                "name": db.get("name"),
            }
            uri = "postgresql://{user}:{pswd}@{host}:{port}/{name}".format(**uri_args)
            cmds = [self.default_cmd, uri]
            proc = self._exec(cmds)
            bak_name = "{database}-{date}.sql".format(database=db.get("name"), date=now)
            self.compress(data=proc.stdout, fname=str(Path(self.backup_dir) / bak_name))

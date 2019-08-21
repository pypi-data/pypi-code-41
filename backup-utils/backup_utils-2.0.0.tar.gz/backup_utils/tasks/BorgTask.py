from ..Task import Task
from ..utils import render
from os import environ


class BorgTask(Task):
    """
    A task to run BorgBackup.

    .. seealso:: Task()
    """

    default_cmd = "borg"

    def _run(self):
        """
        Create a new environment to pass the repo path and password to backup.
        Then execute the backup and prune olf backup.
        """
        borg_env = environ.copy()
        borg_env["BORG_PASSPHRASE"] = self._config.get("pswd", "")
        borg_env["BORG_REPO"] = self._config.get("repo")

        compression = self._config.get("compression", "lzma")
        bak_name = render(self._config.get("name", "::{hostname}-{date}"))
        borg_cmds = [
            self._cmd,
            "create",
            "-v",
            "--stats",
            "--compression",
            compression,
            "--exclude-caches",
            bak_name,
        ]
        borg_cmds.extend(set(self._config.get("directories", [])))
        self._exec(borg_cmds, env=borg_env)

        prune_cmds = [self._cmd, "prune", "-v", "::"]
        prune_cmds.extend(self._config.get("prune", "-d 7 -w 4 -m 3 -y 1").split(" "))
        self._exec(prune_cmds, env=borg_env)

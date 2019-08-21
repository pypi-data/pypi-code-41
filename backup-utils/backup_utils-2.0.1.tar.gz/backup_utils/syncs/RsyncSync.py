from ..Task import Task
from ..utils import render


class RsyncSync(Task):
    """
    A task to synchronize with Rclone.

    .. seealso:: Task()
    """

    default_cmd = "rsync"

    def _run(self):
        """
        Synchronize using repo.
        """
        dist = render(self._config.get("dist", ""))
        repo = self._config.get("repo")

        rsync_cmds = [self._cmd, "-a"]

        if self._config.get("delete", False):
            rsync_cmds.append("--delete")

        excludes = self._config.get("excludes", [])
        if isinstance(excludes, str):
            rsync_cmds.append("--exclude-from={}".format(excludes))
        else:
            for f in excludes:
                rsync_cmds.append("--exclude={}".format(f))
        ssh_opts = self._config.get("ssh_opts", None)
        if ssh_opts:
            rsync_cmds.extend(("-e", ssh_opts))
        rsync_cmds.extend((repo, dist))
        self._exec(rsync_cmds)

from ..Task import Task
from ..utils import render


class RcloneSync(Task):
    """
    A task to synchronize with Rclone.

    .. seealso:: Task()
    """

    default_cmd = "rclone"

    def _run(self):
        """
        Synchronize using repo.
        """
        dist = render(self._config.get("dist", ""))
        repo = self._config.get("repo")
        rclone_cmds = [self._cmd, "-v", "sync", repo, dist]
        self._exec(rclone_cmds)

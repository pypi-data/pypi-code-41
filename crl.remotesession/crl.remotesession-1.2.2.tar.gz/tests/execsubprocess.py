import subprocess
from crl.remotesession.remotesessionbase import RunResult


__copyright__ = 'Copyright (C) 2019, Nokia'


def exec_cmd(cmd, **_):
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         executable='/bin/bash')
    out, err = p.communicate()
    return RunResult(status=str(p.returncode), stdout=out, stderr=err)

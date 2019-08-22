import logging
import shlex
import subprocess

logger = logging.getLogger('statusinfo')


def run_command(cmd):
    args = shlex.split(cmd)
    p = subprocess.Popen(args,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL)
    p.wait(timeout=60)

    stdout, _ = p.communicate()
    stdout = stdout.decode(encoding="UTF-8")
    stdout = stdout.strip()

    return stdout

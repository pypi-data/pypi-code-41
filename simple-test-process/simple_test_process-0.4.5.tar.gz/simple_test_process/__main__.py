from .parseArgs import parseArgs
from .runProcess import runProcess
import sys


def printErr(msg):
    print(msg, file=sys.stderr)


kwargs = parseArgs(*sys.argv[1:]).__dict__
result = runProcess(**kwargs)

if result.stdout:
    print(result.stdout)

if result.stderr:
    printErr(result.stderr)

exit(result.code)

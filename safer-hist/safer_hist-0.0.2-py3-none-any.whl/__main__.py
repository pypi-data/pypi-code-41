import sys
from help import help

if len(sys.argv) <2:
        help()
        sys.exit(1)

commands = [ "genmeta", "lssnaps", "lsuntil", "lsalltime", "restore" ]

if sys.argv[1] in commands:
        module = __import__(sys.argv[1])
        getattr(module,sys.argv[1])()
else:
        help()
import sys

def help():
    print("""Usage: safer subcommand [args ...]

Subcommands list:
help:
  This help summary

lssnaps dataset:
  List snapshots available in given ZFS dataset

genmeta dataset@snap:
  Generate meta-info file for the given ZFS snapshot

lsuntil dataset@snap dir:
  Merged content of given directory for snapshots until the one given 
  (includes deleted entries)

lsalltime dataset@snap dir:
  Merged content of given directory in all snapshots (include deleted 
  and not yet created entries)

restore [-d] dataset@snap dir filename:
  Copy version of filename from given snapshot to current file system, 
  recursively if filename is a directory. When -d flag is given, restore
  is destructive, otherwise conservative.
""")

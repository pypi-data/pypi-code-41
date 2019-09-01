from docopt import docopt
from farmfs import getvol
from fs import Path, userPath2Path
from os import getcwdu

USAGE = \
"""
blobFS

Usage:
  blobfs list
  blobfs s3 list <bucket>

Options:

"""

def main():
  args = docopt(USAGE)
  exitcode = 0
  cwd = Path(getcwdu())
  vol = getvol(cwd)
  if args['list']:
      entries = vol.userdata_csums()
      for entry in entries:
          print entry
  elif args['s3'] and args['list']:
      bucket = args['<bucket>']
      raise NotImplementedError("Need to implement s3 list")

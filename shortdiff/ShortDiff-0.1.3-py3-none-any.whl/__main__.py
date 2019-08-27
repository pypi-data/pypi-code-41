import argparse
from . import create_patch, apply_patch

parser = argparse.ArgumentParser(
        description='Use the ShortDiff differ'
)

parser.add_argument('cmd', metavar='CMD')
parser.add_argument('afile', metavar='FILE_A')
parser.add_argument('bfile', metavar='FILE_B', default=None)

options = parser.parse_args()

cmd = options.cmd
afile = options.afile
bfile = options.bfile

if cmd == 'diff':
    with open(afile) as f:
        txta = f.read()
    if bfile:
        with open(bfile) as f:
            txtb = f.read()
    else:
        from sys import stdin
        txtb = stdin.read()
    print(create_patch(txta, txtb), end='')

elif cmd == 'patch':
    with open(afile) as f:
        patch = f.read()
    if bfile:
        with open(bfile) as f:
            txta = f.read()
    else:
        from sys import stdin
        txta = stdin.read()
    print(apply_patch(txta, patch), end='')
else:
    print('Unkown command')

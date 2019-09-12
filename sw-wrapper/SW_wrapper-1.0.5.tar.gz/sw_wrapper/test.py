import os.path as op
import sys
import os


def main():
    dirs_to_search = list(filter(op.isdir, sys.path))
    for dir in dirs_to_search:
        print(dir)
        so_files = list(filter(lambda x: 'libssw.cpython' in x, os.listdir(dir)))
        if len(so_files) != 0:
            sLibName = so_files[0]
            print(sLibName)
            break


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# Copyright Guanliang MENG 2019-2020
# License: GPL v3
import sys
import os
import argparse
import subprocess
import re


def get_para():

    version = '0.1'

    desc='''
To tar/compress files/directories in batch mode.

By Guanliang Meng, see https://github.com/linzhi2013/batch_tar.

version: {version}
    '''.format(version=version)

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-l', dest='filelst', metavar='<file>',
        help='path list to be dealed with')

    # shoud can be used independently
    parser.add_argument('-L', dest='fileLst', metavar='<str>', nargs='*',
        help='''basenames of files/subdirecotries in `-workdir`.
        If `-workdir` was not specified, `-workdir ./` is assumed.''')

    # another method to find the files
    parser.add_argument('-workdir', metavar='<directory>',
        help='''working directory. must specify `-regex` together''')

    parser.add_argument('-tarfile', metavar='<str>',
        help='''group all the files/subdirecotries into one file.tar
        (.bz2 or .gz). only works with `-L` and `-workdir`''')

    parser.add_argument('-regex', metavar='<str>', default='',
        help="""deal with only the files/subdirecotries in `-l` or `-workdir` whose basenames match the regular expression""")

    # compress or not
    parser.add_argument('-compress', choices=['z', 'j'],
        help='''For the subdirecotries, when executing `tar -cf`,
            also add parameter `z` or `j` for `tar` command. The files
            will always be gzipped if this option was not set.''')

    # delete
    parser.add_argument('-rm', action='store_true',
        help='delete the files/subdirecotries when tar finishs.')

    parser.add_argument('-p', dest='print_only', action='store_true', default=False,
        help='only print out the commands, not run. then you can use qsub-sge.pl to submit multiple jobs. Useful to handle a lot of files because I run in single thread mode only! [%(default)s]')

    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(version))


    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if args.filelst and args.workdir:
        sys.exit('you can not use -l and -workdir at the same time.')

    if args.filelst and args.fileLst:
        sys.exit('`-l` option can not be used with `-L` together!')

    if not args.filelst and not args.fileLst and not args.workdir:
        sys.exit('you must use -l or -L or -workdir')

    if args.filelst and args.tarfile:
        sys.exit('`-l` option can not be used with `-tarfile`!')

    if args.workdir and not args.regex:
        sys.exit('when specify `-workdir`, you must also set `-regex`!')

    if args.fileLst and not args.workdir:
        args.workdir =  os.getcwd()

    if args.workdir:
        args.workdir = os.path.abspath(args.workdir)

    if args.tarfile:
        args.tarfile = re.sub(r'\.tar[(\.gz|\.bz2)]*$', '', args.tarfile)

    return args


def compress_files(filelst=None, compress=None, print_only=False):
    # filelst_abs = [os.path.abspath(f) for f in filelst]
    filelst_abs = filelst
    if compress == 'j':
        cmd = 'bzip2 {0}'.format(' '.join(filelst_abs))
    else:
        cmd = 'gzip {0}'.format(' '.join(filelst_abs))
    if print_only:
        print(cmd)
    else:
        subprocess.check_output(cmd, shell=True)


def tar_direc_and_file(filelst=None, workdir=None, tarfile=None, compress=None, rm=False, print_only=False):
    '''
    if set `tarfile`, all the files/directories will be groupped into
    this file.
    '''

    if not tarfile:
        # from -l or from -workdir and -regex, or -L
        for f in filelst:
            f = re.sub(r'/$', '', f)
            f_abs = os.path.abspath(f)
            f_dir = os.path.dirname(f_abs)
            f_base = os.path.basename(f_abs)

            if os.path.isfile(f_abs):
                compress_files(filelst=[f_abs], compress=compress, print_only=print_only)

            elif os.path.isdir(f_abs):
                # must go to the directory firstly
                cmd = 'cd {f_dir}'.format(f_dir=f_dir)
                if compress == 'z':
                    cmd += ' && tar -zcf {f_base}.tar.gz {f_base}'.format(f_base=f_base)
                elif compress == 'j':
                    cmd += ' && tar -jcf {f_base}.tar.bz2 {f_base}'.format(f_base=f_base)
                else:
                    cmd += ' && tar -cf {f_base}.tar {f_base}'.format(f_base=f_base)
                if rm:
                    cmd += ' && rm -rf {file}'.format(file=f_base)
                if print_only:
                    print(cmd)
                else:
                    subprocess.check_output(cmd, shell=True)

    # from -workdir and -regex, or from -L, and into one tar file
    elif workdir and tarfile:
        # workdir must be abspath
        # becuase filelst is a list of abspath
        workdir = re.sub(r'/$', '', workdir)
        fbase_lst = [re.sub(workdir+'/', '', f) for f in filelst]

        cmd = 'cd {0}'.format(workdir)
        if compress == 'z':
            cmd += ' && tar -zcf {tarfile}.tar.gz {file}'.format(
                tarfile=tarfile,file=' '.join(fbase_lst))
        elif compress == 'j':
            cmd += ' && tar -jcf {tarfile}.tar.bz2 {file}'.format(
                tarfile=tarfile, file=' '.join(fbase_lst))
        else:
            cmd += ' && tar -cf {tarfile}.tar {file}'.format(
                tarfile=tarfile, file=' '.join(fbase_lst))

        if rm:
            cmd += ' && rm -rf {file}'.format(file=' '.join(fbase_lst))

        if print_only:
            print(cmd)
        else:
            subprocess.check_output(cmd, shell=True)


def search_target_files(workdir=None, regex=None):
    results = []
    with os.scandir(workdir) as it:
        for entry in it:
            if re.search(regex, entry.name):
                results.append(os.path.join(workdir, workdir,entry.name))

    return results


def check_file_exists(infile=None, regex='.*'):
    filelst = []
    with open(infile, 'r') as fh:
        for i in fh:
            i = i.strip()
            if os.path.exists(i):
                f = os.path.abspath(i)
                if re.search(regex, f):
                    filelst.append(f)
                else:
                    print('{0} does not match! skip!'.format(i), file=sys.stderr)
            else:
                print('{0} does not exist! skip!'.format(i), file=sys.stderr)

    return filelst


def main():
    args = get_para()

    if args.filelst:
        filelst = check_file_exists(infile=args.filelst, regex=args.regex)

    elif args.workdir and args.regex:
        filelst = search_target_files(workdir=args.workdir, regex=args.regex)
        if args.fileLst:
            filelst.extend(args.fileLst)

    elif args.fileLst:
        filelst = args.fileLst

    else:
        sys.exit('you must set either `-l` or `-L` or `-workdir`, optionaly with `-regex`')

    tar_direc_and_file(
        filelst=filelst,
        workdir=args.workdir,
        tarfile=args.tarfile,
        compress=args.compress,
        rm=args.rm,
        print_only=args.print_only)



if __name__ == '__main__':
    main()
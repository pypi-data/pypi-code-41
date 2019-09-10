#############################################################################
# pristine-lfs
#
# store pristine tarballs in Git LFS
#
# Copyright (C) 2019 Collabora Ltd
# Andrej Shadura <andrew.shadura@collabora.co.uk>

# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later
# version.

# This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License version 2
# text for more details.

# You should have received a copy of the GNU General Public
# License along with this package; if not, write to the Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA  02110-1301 USA
#############################################################################

from gettext import gettext as _
import os
import sys
from . import util
from .util import *
import logging
import argparse
import sh
from fnmatch import fnmatch
from pathlib import Path

from debian import deb822
from debian.changelog import Version, Changelog

from typing import Optional, List

def find_branch(branch: str) -> str:
    if check_branch(branch) is None:
        remote_branches = find_remote_branches(branch)
        if remote_branches:
            commit, branch = remote_branches[0]
        else:
            raise util.Abort(_('No branch {branch} found, not even among remote branches').format(branch=branch))
    return branch

def do_commit(args: argparse.Namespace):
    if check_branch(args.branch) is None:
        if find_remote_branches(args.branch):
            track_remote_branch(args.branch)
    commit_lfs_file(args.tarball, args.branch, args.message, overwrite=args.force_overwrite)

def do_checkout(args: argparse.Namespace):
    branch = find_branch(args.branch)
    os.makedirs(args.outdir, exist_ok=True)
    if args.auto:
        changelog = Path("debian/changelog")
        if not changelog.is_file():
            raise util.Abort(_('file %s not found ') % changelog)
        with changelog.open() as f:
            ch = Changelog(f, max_blocks=1)
        package, version = ch.package, ch.version
    if args.full:
        if not args.auto:
            dsc_file = args.tarball
        else:
            fver = Version(ch.version)
            fver.epoch = None
            dsc_file = f'{package}_{fver}.dsc'
        logging.info(_("Checking out file {} in {}").format(dsc_file, args.outdir))
        checkout_lfs_file(branch, dsc_file, args.outdir)
        if dsc_file.endswith('.dsc'):
            with (Path(args.outdir) / dsc_file).open('r') as dsc:
                d = deb822.Dsc(dsc)
            package = d['Source']
            version = Version(d['Version'])
            files = [f["name"] for f in d["Files"]]
            checkout_package(package, version, branch, args.outdir, files)
    else:
        if not args.auto:
            logging.info(_("Checking out file {} in {}").format(args.tarball, args.outdir))
            checkout_lfs_file(branch, args.tarball, args.outdir)
        else:
            checkout_package(package, version, branch, args.outdir)

def checkout_package(package: str, version: Version, branch: str, outdir: str, requested: Optional[Sequence[str]] = None):
        logging.info(_("Checking out files for {package} version {version} to {outdir}:").format(package=package, version=version, outdir=outdir))
        tarball_glob = f'{package}_{version.upstream_version}.orig.tar.*'
        component_tarball_glob = f'{package}_{version.upstream_version}.orig-*.tar.*'

        files = list_git_files(branch)
        if requested:
            # TODO: handle missing files
            tarballs = [f for f in files if f in requested]
        else:
            tarballs = [f for f in files if fnmatch(f, tarball_glob) or fnmatch(f, component_tarball_glob)]

        os.makedirs(outdir, exist_ok=True)
        for f in tarballs:
            logging.info("         ... {}".format(f))
            checkout_lfs_file(branch, f, outdir)
        logging.info(_("Done."))

def do_list(args: argparse.Namespace):
    branch = find_branch(args.branch)
    for f in list_git_files(branch):
        if f != '.gitattributes':
            print(f)

def do_import(args: argparse.Namespace):
    d = deb822.Dsc(args.dsc)
    package = d['Source']
    version = Version(d['Version'])

    tarball_glob = f'{package}_{version.upstream_version}.orig.tar.*'
    component_tarball_glob = f'{package}_{version.upstream_version}.orig-*.tar.*'
    dsc_dir = os.path.dirname(args.dsc.name)

    if check_branch(args.branch) is None:
        if find_remote_branches(args.branch):
            track_remote_branch(args.branch)

    tarballs = [os.path.join(dsc_dir, f['name']) for f in d['Files'] if args.full or fnmatch(f['name'], tarball_glob) or fnmatch(f['name'], component_tarball_glob)]
    if args.full:
        tarballs += [args.dsc.name]

    if tarballs:
        logging.info("Importing: %s" % " ".join(tarballs))
        commit_lfs_files([open(tarball, 'rb') for tarball in tarballs], args.branch, args.message, overwrite=args.force_overwrite)

def main():
    prog = os.path.basename(sys.argv[0])

    parser = argparse.ArgumentParser(description=_('store pristine tarballs in Git LFS'), prog=prog)
    parser.add_argument('-v', '--verbose', action='count', help=_('be more verbose'))
    parser.add_argument('--debug', action='store_const', const=2, dest='verbose', help=_('be debuggingly verbose'))
    parser.set_defaults(verbose=0, func=lambda x: parser.print_usage(file=sys.stderr))
    subparsers = parser.add_subparsers(required=False)

    parser_commit = subparsers.add_parser('commit', help=_('commit a tarball'))
    parser_commit.add_argument('--force-overwrite', action='store_true', help=_('overwrite already stored files'))
    parser_commit.add_argument('-m', '--message', default=None, help=_('commit message'))
    parser_commit.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_commit.add_argument('tarball', type=argparse.FileType('rb'), help=_('tarball to commit'))
    parser_commit.add_argument('upstream', nargs='?', default=None, help=_('ignored'))
    parser_commit.set_defaults(func=do_commit)

    # we have to do some trickery since argparse doesn’t support this syntax natively
    parser_checkout = subparsers.add_parser('checkout', help=_('checkout a tarball'))
    parser_checkout.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_checkout.add_argument('--full', default=False, action='store_true', help=_('also check out all related files of the Debian package'))
    parser_checkout.add_argument('-o', '--outdir', default='.', help=_('output directory for the tarball'))
    checkout_group = parser_checkout.add_mutually_exclusive_group(required=True)
    checkout_group.add_argument('--auto', default=False, action='store_true', help=_('check out all tarballs required by the currently checked out Debian package'))
    checkout_group.add_argument('tarball', nargs='?', default=None, help=_('tarball to check out'))
    parser_checkout.set_defaults(func=do_checkout)

    parser_list = subparsers.add_parser('list', help=_('list tarballs stored in the repository'))
    parser_list.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_list.set_defaults(func=do_list)

    parser_import = subparsers.add_parser('import-dsc', help=_('import tarballs and their signatures from a .dsc'))
    parser_import.add_argument('dsc', type=argparse.FileType('r'), help='.dsc file to use')
    parser_import.add_argument('--force-overwrite', action='store_true', help=_('overwrite already stored files'))
    parser_import.add_argument('--full', default=False, action='store_true', help=_('also import all related files of the Debian package'))
    parser_import.add_argument('-m', '--message', default=None, help=_('commit message'))
    parser_import.add_argument('-b', '--branch', default='pristine-lfs', help=_('branch to store metadata on'))
    parser_import.set_defaults(func=do_import)

    args = parser.parse_args()

    logging.basicConfig(format='{levelname[0]}: {message!s}', style='{', level=(logging.WARNING - 10 * args.verbose))

    # sh is printing debug on the info channel
    logging.getLogger(sh.__name__).setLevel(logging.WARNING - 10 * (args.verbose - 1))

    try:
        args.func(args)
    except sh.ErrorReturnCode as e:
        print(_('Failed to run %s:') % e.full_cmd, file=sys.stderr)
        print(e.stderr.decode(sh.DEFAULT_ENCODING, "replace"), file=sys.stderr)
        sys.exit(e.exit_code)
    except KeyboardInterrupt as e:
        print(file=sys.stderr)
        print(_('about: Interrupted by user'), file=sys.stderr)
        sys.exit(1)
    except util.Abort as e:
        print(_("abort: %s\n") % e, file=sys.stderr)
        sys.exit(1)

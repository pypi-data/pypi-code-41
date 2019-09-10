#############################################################################
# pristine-lfs
#
# Git and Git LFS routines
# This requires Git and git-lfs to be installed.
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
import logging
import sh
import sh.contrib
import os
from pathlib import Path
from fnmatch import fnmatchcase
from contextlib import contextmanager

from typing import Optional, Tuple, List, Sequence, IO, Any, Union, Mapping

gitattributes = """*.tar.* filter=lfs diff=lfs merge=lfs -text
*.tar.*.asc -filter -diff merge=binary -text
*.dsc -filter !diff merge=binary !text
"""

pre_push_hook = """#!/bin/sh -e

case "$GIT_LFS_SKIP_PUSH" in
    true | on | 1)
        exit 0
        ;;
    *)
        git lfs pre-push "$@"
        ;;
esac
"""

def git(*args, index: Optional[Path] = None, **kwargs):
    e = os.environ
    if index:
        e["GIT_INDEX_FILE"] = str(index)
    return sh.contrib.git(*args, **kwargs, _env=e)

git.lfs = sh.contrib.git.lfs

@contextmanager
def open_index(name: str) -> Path:
    index = Path(git_dir()) / f"index-{name}"
    if index.exists():
        index.unlink()
    try:
        yield index
    finally:
        if index.exists():
            index.unlink()

AttributeValue = Union[str, bool, None]

def parse_attr(attr: str) -> Tuple[str, AttributeValue]:
    """
    Parse a git attribute into its value:

    >>> parse_attr('attr')
    ('attr', True)
    >>> parse_attr('-attr')
    ('attr', False)
    >>> parse_attr('!attr')
    ('attr', None)
    >>> parse_attr('attr=text')
    ('attr', 'text')
    """
    if attr.startswith('!'):
        return attr[1:], None
    if attr.startswith('-'):
        return attr[1:], False
    if '=' not in attr:
        return attr, True
    return tuple(attr.split('='))

def parse_git_attributes(s: str) -> List[Tuple[str, Mapping[str, AttributeValue]]]:
   lines = [l.strip() for l in s.splitlines()]
   lines = [l.split() for l in lines if len(l) and not l.startswith('#')]
   return [(l[0], {k: v for k, v in [parse_attr(a) for a in l[1:]]}) for l in lines if len(l)]

default_gitattributes = parse_git_attributes(gitattributes)

class Abort(Exception):
    pass

def check_branch(name: str) -> Optional[str]:
    """
    Check a branch exists, return the hash it points at, if it does.

    None if there’s no such branch
    """
    try:
        return git('show-ref', '--heads', '--hash', '--', name)
    except sh.ErrorReturnCode:
        return None

def git_dir() -> str:
    return git('rev-parse', '--git-dir').strip('\n')

def git_head() -> str:
    return git('rev-parse', '-q', '--verify', '--symbolic-full-name', 'HEAD', _ok_code=[0, 1]).strip('\n')

def find_remote_branches(name: str) -> List[Tuple[str, str]]:
    try:
        branches = [l.split(' ') for l in git('show-ref', '--', name).splitlines()]
        return [(b[0], b[1]) for b in branches if b[1].startswith('refs/remotes/')]
    except sh.ErrorReturnCode:
        return []

def track_remote_branch(name: str):
    remote_branches = find_remote_branches(name)
    if len(remote_branches) == 0:
        raise RuntimeError('remote branch expected but not found')
    commit, branch = remote_branches[0]
    git('branch', '--track', name, branch)

def store_lfs_object(io: Any) -> str:
    return str(git.lfs.clean(io.name, _in=io))

def store_git_object(io: Any) -> str:
    return git('hash-object', '-w', '--stdin', _in=io).strip('\n')

def stage_file(filename: Union[str, bytes], io: Any, index: Path = None):
    blob = store_git_object(io)
    if isinstance(filename, bytes):
        filename = filename.decode()
    git('update-index', '--add', '--replace', '--cacheinfo', "100644,%s,%s" % (blob, filename), index=index)

def create_commit(branch: str, message: str, index: Path = None) -> str:
    tree = git('write-tree', index=index).strip('\n')
    if not len(tree):
        raise RuntimeError('write-tree failed')

    if check_branch(branch) is not None:
        commit = git('commit-tree', tree, '-p', branch, _in=message).strip('\n')
    else:
        commit = git('commit-tree', tree, _in=message).strip('\n')
    if not len(commit):
        raise RuntimeError('commit-tree failed')

    git('update-ref', 'refs/heads/%s' % branch, commit)

    return commit

def parse_diff_entry(entry: str) -> Mapping[str, str]:
    treediff, names = entry.split('\t', maxsplit=1)
    srcmode, dstmode, srchash, dsthash, status = treediff.lstrip(':').split(' ')
    srcname, _, dstname = names.partition('\t')
    return {
        'srcmode': srcmode,
        'dstmode': dstmode,
        'srchash': srchash,
        'dsthash': dsthash,
        'srcname': srcname,
        'dstname': dstname,
        'status': status,
    }

def commit_lfs_file(io: IO[bytes], branch: str, template: str = None, overwrite: bool = False):
    """
    Store the file in the LFS storage and commit it to a branch.
    """
    commit_lfs_files([io], branch)

def commit_lfs_files(ios: Sequence[IO[bytes]], branch: str, template: str = None, overwrite: bool = False):
    """
    Store the files in the LFS storage and commit them to a branch.
    """
    # make sure the pre-push hook has been set up
    hook_path = Path(git_dir()) / 'hooks' / 'pre-push'
    if not hook_path.is_file():
        try:
            hook_path.parent.mkdir(exist_ok=True)
            hook_path.write_text(pre_push_hook)
            hook_path.chmod(0o755)
        except IOError as e:
            logging.warning(_('Failed to set up pre-push hook: %s') % e.strerror)

    with open_index("pristine-lfs") as index:
        # make sure we include all previously committed files
        if check_branch(branch) is not None:
            git(git('ls-tree', '-r', '--full-name', branch), 'update-index', '--index-info', index=index)

        # make sure .gitattributes is present
        stage_file('.gitattributes', gitattributes, index=index)

        for io in ios:
            filename = os.path.basename(io.name)
            if not is_lfs_managed(os.path.basename(filename), default_gitattributes):
                stage_file(filename, io, index=index)
            else:
                metadata = store_lfs_object(io)
                stage_file(filename, metadata, index=index)

        if check_branch(branch) is not None:
            diff = git('diff-index', '--cached', branch).strip().splitlines()
            if not diff:
                logging.info(_("Nothing to commit"))
                return
            parsed_diff = [parse_diff_entry(d) for d in diff]
            overwritten = [d['srcname'] for d in parsed_diff if d['srchash'] != ('0' * 40) and d['srcname'] != '.gitattributes']
            if any(overwritten) and not overwrite:
                raise Abort(_('would overwrite files: %s') % ', '.join(overwritten))

        if not template:
            template = "pristine-lfs data for %s"

        message = template % ', '.join([os.path.basename(io.name) for io in ios])

        commit = create_commit(branch, message, index=index)

        # if the branch is currently checked out, reset it
        if git_head() == f'refs/heads/{branch}':
            git('reset', '--hard')

def list_lfs_files(branch: str) -> List[str]:
    return git.lfs('ls-files', '--name-only', branch).splitlines()

def parse_entry(entry: str) -> Tuple[str, ...]:
    info, name = entry.split('\t')
    mode, type, hash = info.split(' ')
    return mode, type, hash, name

def list_git_files(branch: str) -> Mapping[str, str]:
    entries = [parse_entry(l) for l in git('ls-tree', '-r', '--full-name', branch).splitlines()]
    return {e[3]: e[2] for e in entries if e[1] == 'blob'}

def is_lfs_managed(filename: str, attributes: List[Tuple[str, Mapping[str, AttributeValue]]]):
    lfs_managed = False
    for pattern, attrs in attributes:
        if fnmatchcase(filename, pattern):
            if 'filter' in attrs:
                lfs_managed = attrs['filter'] == 'lfs'
    return lfs_managed

def checkout_lfs_file(branch: str, filename: str, outdir: str = '.'):
    files = list_git_files(branch)
    if '.gitattributes' in files:
        attributes = parse_git_attributes(git('cat-file', 'blob', files['.gitattributes']))
    else:
        attributes = []

    if filename not in files:
        raise Abort(_('%s not found on branch %s') % (filename, branch))

    with (Path(outdir) / filename).open(mode='wb') as tarball:
        if is_lfs_managed(filename, attributes):
            metadata = git('cat-file', 'blob', files[filename])
            git.lfs.smudge(filename, _out=tarball, _in=metadata)
        else:
            git('cat-file', 'blob', files[filename], _out=tarball)

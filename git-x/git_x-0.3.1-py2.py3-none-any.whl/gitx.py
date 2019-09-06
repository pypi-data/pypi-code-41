# -*- coding: utf-8 -*-

import argparse
from utils import *
import os


class Gitx:
    def __init__(self):
        pass

    def st(self):
        call('git status')

    def p(self):
        cmd = 'git pull --rebase'
        print_info("Pull latest code ...[{}]".format(cmd))
        call(cmd)

    def up(self):
        current_branch = self._current_branch()
        call("git push --set-upstream origin {}".format(current_branch))

    def co(self, branch, start_point=None, create_if_not_existed=False):
        print_info('Checking out {} ... '.format(branch))
        create_option = " -b" if create_if_not_existed else ''

        st_point = start_point if start_point and create_if_not_existed else ''

        branches = [each.lstrip('*').strip() for each in popen('git branch').splitlines()]

        if not create_if_not_existed:
            matches = [each for each in branches if branch in each]
            if len(matches) == 1:
                print_info('Matched a branch {}'.format(matches[0]))
                branch = matches[0]
            elif len(matches) > 1:
                print_info('Found {} branches including {}:'.format(len(matches), quote(branch)))
                print_info('='*20)
                for index, each in enumerate(matches):
                    print_info('{}: {}'.format(index, each))
                print_info('='*20)
                index = print_prompt('Please select branch by index', type_=int)
                branch = matches[index]
            else:
                pass  # let git itself handle this.

        command = 'git checkout{} {} {}'.format(create_option, branch, st_point).strip()
        call(command)

    def a(self, include, exclude):
        include_str = ' '.join([quote(each) for each in include]) if isinstance(include, list) else quote(include)
        if include_str:
            call('git add {}'.format(include_str))

        exclude_str = ' '.join([quote(each) for each in exclude]) if isinstance(exclude, list) else quote(exclude)
        if exclude_str:
            call('git reset {}'.format(exclude_str))

    def ci(self, comment, include, exclude):
        if comment is None or comment == '':
            raise Exception(error('Please add a valid comment.'))

        self.a(include, exclude)

        call('git commit -m {}'.format(quote(comment)))

    def amend(self, include, exclude, edit):
        self.a(include, exclude)
        cmd = 'git commit --amend --no-edit' if not edit else 'git commit --amend'
        call(cmd)

    def cia(self, comment, exclude):
        if comment is None or comment == '':
            raise Exception(error('Please add a valid comment.'))
        self.a('.', exclude)
        call('git commit -m "{}"'.format(comment))

    def llg(self, n=5, g=False, a=False, d=False):
        if n <= 0:
            raise Exception(error('The commit count must be greater than zero.'))

        cmd = 'git log {} --pretty=format:"{} {} %s{}{}" --abbrev-commit -n {}'\
            .format(
                    '--graph' if g else '--oneline',
                    '%C(auto)%h%Creset',
                    '%C(auto)%d%Creset',
                    ' %Cgreen(%cr)%Creset' if d else '',
                    ' %C(cyan)<%an>%Creset' if a else '',
                    n)
        call(cmd)

    def pr(self, to_branch):

        remote_url = self._remote_url()
        if remote_url.endswith('.git'):
            remote_url = remote_url[:-4]
        current_branch = self._current_branch()
        if to_branch == current_branch:
            print_error("Can't create pull request against the same branch")
            exit()
        else:
            print_info("Creating PR from {} to {}".format(current_branch, to_branch))

        old_start = "git@"
        if remote_url.startswith(old_start):
            remote_url = remote_url.replace(':', '/', 1)
            remote_url = remote_url.replace(old_start, "https://")

        if remote_url.find('github.com') >= 0:
            pr_url = "{}/compare/{}...{}?expand=1".format(remote_url, to_branch, current_branch)
        elif remote_url.find('bitbucket.org') >= 0:
            pr_url = "{}/compare/{}%0D{}".format(remote_url, current_branch, to_branch)
        else:
            raise Exception("Don't know how to generate the pull request url..")

        open_url(pr_url)

    def m(self, _from):
        if _from is None:
            raise error("Please input source branch")

        _from = _from.strip()
        if len(_from.split()) > 1:
            raise Exception("Invalid parameter.")

        currentBranch = self._current_branch()

        self.co(_from)
        self.p()
        print_info("Go back to {}.".format(currentBranch))
        os.system('git checkout {}'.format(currentBranch))

        print_info('Merging the latest code from {} to {} ...'.format(_from, currentBranch))
        os.system("git merge {}".format(_from))

    def b(self):
        self._current_branch()

    def _current_branch(self):
        branch = popen('git rev-parse --abbrev-ref HEAD')
        print_info('Current branch: {}'.format(branch))
        return branch

    def _remote_url(self):
        cmd = "git config --get remote.origin.url"
        remote_url = popen(cmd)
        print_info('Remote origin url: {}'.format(remote_url))
        return remote_url

    def _branches_with_name_like(self, str):
        cmd = 'git branch'
        branches = popen(cmd)
        print(branches)

    def clb(self):
        current_branch = self._current_branch()
        branches_ignored = ['master', 'dev', 'develop', 'trunk', current_branch]
        cmd = 'git branch --merged'
        merged_local_branches = [each.lstrip('*').strip() for each in popen(cmd).splitlines()]
        branches_to_clean = set(merged_local_branches) - set(branches_ignored)

        if len(branches_to_clean) == 0:
            return

        print_info('Found {} branches to delete:'.format(len(branches_to_clean)))
        print_info('=' * 20)
        for branch in branches_to_clean:
            print_info(branch)
        print_info('=' * 20)

        for branch in branches_to_clean:
            self._delete_branch(branch)
        else:
            print_info("All done.")

    def _delete_branch(self, branch):
        yes = print_confirm("Do you want to delete branch [ {} ]? ".format(branch))
        if yes:
            failed = call('git branch --delete {}'.format(branch), exit_on_error=False)
            if not failed:
                print_info('branch [ {} ] is deleted.'.format(branch))
            else:
                forced = print_confirm("Do you want to force delete branch [ {} ]? ".format(branch), default=False)
                if forced:
                    call('git branch -D {}'.format(branch))
                    print_info('branch [ {} ] is deleted.'.format(branch))
                else:
                    print_info('skipped.')
        else:
            print_info('skipped.')


def init_parser():
    parser = argparse.ArgumentParser(description='git extensions',
                                     epilog=info('Try the green command listed above'))
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-st", "--status", action="store_true", help=info("git st"))
    group.add_argument("-p", "--pull", action="store_true", help=info("git p"))
    group.add_argument("-llg", "--logn", help=info("git llg [n]"))
    group.add_argument("-m", "--merge", help=info("git m [from]"))
    return parser


def main():
    parser = init_parser()
    args = parser.parse_args()
    gitx = Gitx()

    if args.status:
        gitx.st()
    elif args.pull:
        gitx.p()
    elif args.logn:
        gitx.llg(args.logn)
    elif args.merge:
        gitx.m(args.merge)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

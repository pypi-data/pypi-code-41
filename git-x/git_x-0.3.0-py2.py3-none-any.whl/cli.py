"""
git-x - a set of handy git extensions.

"""

__version__ = "0.3.0"
__author__ = "Qingshan Zhuan"
__license__ = "MIT"

import click

from gitx import Gitx

CONTEXT_SETTINGS = dict(help_option_names=['-h'])


@click.command(short_help="Add file contents to the index")
@click.argument("pathspec", nargs=-1, metavar='<pathspec>')
@click.option("-x", '--exclude',
              metavar='<pathspec>',
              multiple=True,
              help="Exclude the files that match the pattern(same as the <pathspec> for 'git add' command)")
def a(pathspec, exclude):
    """
    \b
    Add file that specified in <pathspec> contents into the index.
    Ignore/Remove the file contents from the index if the files are specified in the -x option.
    The <pathspec> syntax is same as the one in 'git status' parameter.
    \b
    Examples:
        1. Add all sql files:
            git a *.sql
        2. Add all files, but ignore all config files(ending with .config extensions)
            git a . -x *.config
        3. Ignore multiple files(*.config, *.md) by using more than one '-x' to specify multiple patterns.
            git a . -x *.config -x *.md
        4. Remove all config files from the index
            git -x *.config
    """
    Gitx().a(list(pathspec), list(exclude))


@click.command(short_help="Amend files into repository")
@click.option('-e', '--edit', is_flag=True, show_default=True, help="Prompt edit window")
def amend(edit):
    """
    \b
    Amend files into repository, this only amend the files that already in the index.
    \b
    Examples:
        1. Amend without editing
            git amend
        2. Amend, and edit the commit message, this will open the editing window,
            depends on what editor is configured in git.
            git amend -e

    """
    Gitx().amend(None, None, edit)


@click.command(short_help='Show current branch name')
def b():
    """
    \b
    Show current branch name.
    \b
    Example:
        git b
    """
    Gitx().b()


@click.command(short_help='Clean merged local branch.')
def clb():
    """
    \b
    Clean merged local branch.
    It will always let user to confirm before remove.
    By default, it will ignore current branch and branches with name master, dev, develop, trunk.
    Because those branches are mostly used as trunk/release branches.
    \b
    """
    Gitx().clb()


@click.command(short_help="Commit all the indexed files")
@click.argument('comment', metavar='<comment>')
def ci(comment):
    """
    \b
    Commit all the indexed files into repository, same as 'git commit -m <comment>'.
    \b
    Example:
        git ci "This is the comment."
    """
    Gitx().ci(comment, None, None)


@click.command(short_help="Add files into index and commit")
@click.argument('comment', metavar='<comment>')
@click.option('-x', '--exclude', metavar='<pathspec>', required=False, multiple=True)
def cia(comment, exclude):
    """
    \b
    Add content files into index, and then create a new commit.
    By default it will add all the files under the current folder.
    You can ignore/remove files by specifying in the '-x' option.
    This is a combination of the following commands:
    `git a . -x <pathspec>`
    `git commit -m <comment>`
    \b
    Examples:
        1. Add all files and create a commit.
            git cia "This is the comment"
        2. Exclude *.config files, and create a commit.
            git -x *.config "This is the comment"
        3. Exclude the *.cs and *.config files, and create a commit.
            git -x *.config -x *.cs "This is the comment"
    """
    Gitx().cia(comment, list(exclude))


@click.command(short_help="Checkout/Create branch")
@click.option('-b', metavar='create_if_not_existed', required=False,
              is_flag=True,
              show_default=True,
              help="Indicate to create the branch if it doesn't exist, same to '-B' option in 'git checkout' command.")
@click.argument('branch', metavar='<branch>')
@click.argument('start_point', metavar='<start_point>', required=False)
def co(start_point, b, branch):
    """
    \b
    Check out the branch matching the string in <branch>.
    If multiple branches include the <branch> text, all those branches will be listed and let user to choose.
    This only works if '-b' is not present.
    If '-b' is present, a new branch with name <branch> will be created.
    \b
    Examples:
        Suppose we have 4 existing branches - master, develop, feature_1, feature_2
        1. Switch to an existing branch 'develop'
            git co develop
        2. Create a new branch 'feature_3'
            git co -b feature_3
        3. Create a new branch, and set the start point with <start_point>
            git co -b feature_3 32aa51b
        4. Switch to a branch with name like 'feature_*'
            gi co feature_
            \b
            Then it will list all indexed branches with 'feature_' in the name, and let the user to choose:
            \b
            Found 4 branches including "feature_":
            ====================
            0: feature_1
            1: feature_2
            ====================
            Please select branch by index:
            \b
            Then, the user can choose 0, click ENTER to switch to feature_1 branch.
    """
    print(branch, b, start_point)
    Gitx().co(branch, start_point, b)


@click.command(short_help="Show recent <number> logs", )
@click.argument('n', metavar='<number>', default=5)
@click.option('-g', '--graph', is_flag=True, required=False, help='Show in graph mode')
@click.option('-a', '--author', is_flag=True, required=False, help='Show the author name of each commit')
@click.option('-d', '--date', is_flag=True, required=False, help='show relative date of each commit')
def llg(n, graph, author, date):
    """
    \b
    Show recent <number> logs, the default number is 5.
    This is same as 'git log --oneline -n <number>'
    \b
    Example:
        1. Show recent 5 commit messages.
            git llg
        2. Show recent 6 commit messages.
            git llg 6
        3. Show with graph
            git llg -g
        4. Show with graph, author, and date
            git llg -gad
    """
    Gitx().llg(n, graph, author, date)


@click.command(short_help="Merge codes from branch <from> to current branch")
@click.argument('from_', metavar='<from>')
def m(from_):
    """
    \b
    Merge codes from branch <from> to current branch.
    It will switch to branch <from>, pull the latest code, and then switch back to previous branch,
    and merge the code from <from> into current branch. You need to make sure that there is no unstaged changes.
    \b
    Examples:
        1. Merge latest code from master branch to current branch(develop)
            git m master
    """
    Gitx().m(from_)


@click.command(short_help='Pull latest code')
def p():
    """
    \b
    Pull the latest code from remote  with '--rebase' option.
    It is same as 'git pull --rebase'
    """
    Gitx().p()


@click.command(short_help='Create pull request from current branch to <to_branch>')
@click.argument('to_branch', metavar='<to_branch>', nargs=1)
def pr(to_branch):
    """
    \b
    Create pull request from current branch to <to_branch>.
    Currently it only support to raise pull request to github and bitbucket.
    The repository url is retrieved from the .git/config file.
    \b
    Examples:
        1. Create PR against master branch
            git pr master
    """
    Gitx().pr(to_branch)


@click.command(short_help="Show the working tree status")
def st():
    """
    \b
    Show the working tree status, same as 'git status'
    """
    Gitx().st()


@click.command(short_help="Create remote branch")
def up():
    """
    \b
    Create remote branch,
    same as 'git push --set-upstream origin'
    """
    Gitx().up()


@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    pass


def all_commands():
    return [a, amend, b, ci, cia, clb, co, llg, m, p, pr, st, up]


for each in all_commands():
    each.context_settings = CONTEXT_SETTINGS
    main.add_command(each)

if __name__ == '__main__':
    main()

import configparser
import os
import time

import click

from dsa import dsa_problem_file
from dsa.dsa_problem import load_problem
from hackerrank import hackerrank
from hackerrank.hackerrank import HackerRank
from helpers.clog import CLog


@click.group()
def cli():
    """
    Problem Toolbox - Problem CLI tools by Thuc Nguyen (https://github.com/thucnc)
    """
    click.echo("Problem Toolbox - Problem CLI tools by Thuc Nguyen (https://github.com/thucnc)")


@cli.group(name='dsa')
def dsa_group():
    """
    DSA problem tools
    """
    click.echo("Common DSA tools")


@cli.group(name='hackerrank')
def hackerrank_group():
    """
    Hackerrank tools
    """
    click.echo("hackerrank.com tools")


@dsa_group.command()
@click.option('-d', '--dir', default='.',
              type=click.Path(file_okay=False),
              prompt='Base directory for the problem', help='Base folder for the problem')
@click.option('--overwrite/--no-overwrite', default=False, help='Overwrite existing folder, default - No')
@click.argument('problem', metavar='{problem}')
def create_problem(dir, overwrite, problem):
    """
    Create a problem boilerplate

    Syntax:
    ptoolbox dsa create-problem -d {folder} {problem-code} [--overwrite]

    Ex.:
    ptoolbox dsa create-problem -d problems/ prob2 --overwrite

    """
    dsa_problem_file.create_problem(dir, problem, overwrite=overwrite)


@dsa_group.command()
@click.option('--autofix/--no-auto-fix', default=False, help='Auto fix style, save original file to .bak.md, default - No')
@click.argument('problem_folder', metavar='{problem_folder}')
def check_problem(autofix, problem_folder):
    """
    Check problem folder for proper format

    Syntax:
    ptoolbox dsa check-problem {problem-folder}

    Ex.:
    ptoolbox dsa check-problem ../problems/prob2

    """
    dsa_problem_file.check_problem(problem_folder, autofix)


@hackerrank_group.command()
@click.option('--keep-zip-file-only/--keep-intermediate-files', default=True,
              help='Remove intermediate files, default - Yes')
@click.argument('problem_folder', metavar='{problem_folder}')
def prepare_testcases(keep_zip_file_only, problem_folder):
    """
    Convert testcases to hackerrank format, and compress into .zip file, ready for upload

    Syntax:
    ptoolbox hackerrank prepare-testcases  {problem-folder} [--keep-zip-file-only/--keep-intermediate-files]

    Ex.:
    ptoolbox hackerrank prepare-testcases problems/prob2

    """
    hackerrank.prepare_testcases(problem_folder, keep_zip_file_only=keep_zip_file_only)


def read_username_password(credential_file):
    config = configparser.ConfigParser()
    config.read(credential_file)
    if not config.has_section('HACKERRANK'):
        CLog.error(f'Section `HACKERRANK` should exist in {credential} file')
        return None, None
    if not config.has_option('HACKERRANK', 'username') or not config.has_option('HACKERRANK', 'password'):
        CLog.error(f'Username and/or password are missing in {credential} file')
        return None, None

    username = config.get('HACKERRANK', 'username')
    password = config.get('HACKERRANK', 'password')

    return username, password


@hackerrank_group.command()
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.option('--with-testcases/--without-testcases', default=True, help='Upload testcases')
@click.option('-w', '--weight', default=100, type=click.INT, help='Weight (score) of each testcase')
@click.option('-s', '--sample', default=1, type=click.INT, help='Number of sample testcases')
@click.argument('problem_folder', metavar='{problem_folder}')
def create_problem(credential, with_testcases, weight, sample, problem_folder):
    """
    Create problem description on hackerrank

    Syntax:
    ptoolbox hackerrank create-problem [--upload-testcases] {dsa_problem_folder}

    Ex.:
    ptoolbox hackerrank create-problem problems/array001_counting_sort3/

    """
    username, password = read_username_password(credential)
    if not username or not password:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    hr = HackerRank()
    hr.login(username, password)

    problem1 = load_problem(problem_folder)
    hk_problem = hr.create_problem(problem1)

    if hk_problem and with_testcases:
        _do_upload_testcases(username, password, weight, sample, hk_problem["id"], problem_folder)

    # print(hk_problem)

    if problem1:
        CLog.important(f'Problem `{hk_problem["id"]}` updated, slug: {hk_problem["slug"]}')


@hackerrank_group.command()
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.argument('hackerrank_problem_id', metavar='{hackerrank_problem_id}')
@click.argument('problem_folder', metavar='{problem_folder}')
def update_problem(credential, hackerrank_problem_id, problem_folder):
    """
    Update problem description on hackerrank

    Syntax:
    ptoolbox hackerrank update-problem {hackerrank_problem_id} {dsa_problem_folder}

    Ex.:
    ptoolbox hackerrank update-problem 113357 problems/array001_counting_sort3/

    """
    username, password = read_username_password(credential)
    if not username or not password:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    hr = HackerRank()
    hr.login(username, password)

    problem1 = load_problem(problem_folder)

    hk_problem = hr.update_problem(hackerrank_problem_id, problem1)

    # print(hk_problem)

    if problem1:
        CLog.important(f'Problem `{hk_problem["id"]}` updated, slug: `{hk_problem["slug"]}`')


def _do_upload_testcases(username, password, weight, sample, hackerrank_problem_id, problem_folder):
    testcase_zip = os.path.join(problem_folder, 'testcases_hackerrank.zip')

    if not os.path.exists(testcase_zip):
        CLog.error(f'`{testcase_zip}` does not exist, '
                   f'please run `ptoolbox hackerrank prepare-testcases {problem_folder}` first')
        return

    hr = HackerRank()
    hr.login(username, password)
    created_testcases = hr.upload_testcases_and_set_score(hackerrank_problem_id, testcase_zip, weight, sample)

    print(created_testcases)

    if created_testcases:
        CLog.important(f'{len(created_testcases)} test cases uploaded to problem `{hackerrank_problem_id}`')


@hackerrank_group.command()
@click.option('-c', '--credential', default='credentials.ini',
              type=click.Path(dir_okay=False, exists=True),
              prompt='Credential file', help='Configuration file that contain hackerrank user name/pass')
@click.option('-w', '--weight', default=100, type=click.INT, help='Weight (score) of each testcase')
@click.option('-s', '--sample', default=1, type=click.INT, help='Number of sample testcases')
@click.argument('hackerrank_problem_id', metavar='{hackerrank_problem_id}')
@click.argument('problem_folder', metavar='{problem_folder}')
def upload_testcases(credential, weight, sample, hackerrank_problem_id, problem_folder):
    """
    Upload testcases_hackerrank.zip to problem on hackerrank

    Syntax:
    ptoolbox hackerrank upload-testcases -w {weight} -s {sample_count} {hackerrank_problem_id} {dsa_problem_folder}

    Ex.:
    ptoolbox hackerrank upload-testcases -w 100 -s 2 113357 problems/array001_counting_sort3/

    """
    username, password = read_username_password(credential)
    if not username or not password:
        CLog.error(f'Username and/or password are missing in {credential} file')
        return

    _do_upload_testcases(username, password, weight, sample, hackerrank_problem_id, problem_folder)

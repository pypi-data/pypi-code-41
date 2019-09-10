#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © %YEAR%  <>
#
# Distributed under terms of the %LICENSE% license.

"""
Tool for easy push project to pypi and binstar (Anaconda).
Git pull, bumpversion, pip build and upload, conda build and upload and git push is performed.
There is also option to init new project directory.

"""

# import logging
# logger = logging.getLogger(__name__)
from loguru import logger
import argparse
import subprocess
import os
import os.path as op
import shutil
import glob
from pathlib import Path
from . import file_content

__version__ = "2.4.0"


def mycall(command, ignore_error=True):
    if type(command) is list:
        try:
            # subprocess.call(command)
            subprocess.check_call(command)
        except subprocess.CalledProcessError as e:
            if ignore_error:
                logger.warning("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            else:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    else:
        try:
            # subprocess.call(command, shell=True)
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as e:
            if ignore_error:
                logger.warning("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
            else:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


def check_git():
    try:
        import git
        import git.exc
    except:
        logger.info("GitPython is not installed")
        return

    try:
        repo = git.Repo(".")
    except git.exc.InvalidGitRepositoryError as e:
        logger.info("It is not Git repo")


    if repo.is_dirty():
        logger.error("Git working directory is dirty. Clean it.")
        exit()

def make(args):
    if op.exists("meta.yaml"):
        # old position of recipe
        prefix = "conda-recipe/"
    else:
        prefix = ""

    if not op.exists("conda-recipe"):
        import os
        os.makedirs("conda-recipe")
    if not op.exists(prefix + "build.sh"):
        with open(prefix + 'build.sh', 'a') as the_file:
            the_file.write('#!/bin/bash\n\n$PYTHON setup.py install\n')
    if not op.exists(prefix + "bld.bat"):
        with open(prefix + 'bld.bat', 'a') as the_file:
            the_file.write('"%PYTHON%" setup.py install\nif errorlevel 1 exit 1')

    check_git()
    if (args.action == "init"):
        init(args) #, author=args.author, email=args.email, githubuser=args.gihubuser)
        return
    elif (args.action == "stable"):
        mycall("git push --tags")
        mycall("git checkout stable")
        mycall("git pull origin master")
        mycall("git push")
        mycall("git checkout master")
        return
    elif args.action in ["minor", "major", "patch"]:
        if not args.skip_git:
            logger.debug("pull, patch, push, push --tags")
            mycall("git pull")
        if args.skip_bumpversion:
            logger.info("skip bumpversion")
        else:
            mycall("bumpversion " + args.action)
            if not args.skip_git:
                mycall("git push")
                mycall("git push --tags")
        # if args.init_project_name is "pypi":
        #     upload_conda = False
    elif args.action in ["stay"]:
        logger.debug("stay on version")
    # elif args.action in ["build_conda"]:
    #     logger.debug("build conda based on meta.yaml")
    #     process_pypi = False
    elif args.action in ["skeleton"]:
        logger.debug("building skeleton")
        package_name = args.project_name
        mycall(["conda", "skeleton", "pypi", package_name], ignore_error=False)
        return
    else:
        logger.error("Unkown command '"+ args.action + "'")
        return

# fi
    # upload to pypi
    if not args.skip_pypi:
        pypi_build_and_upload(args)


    pythons = args.py
    if len(args.py) == 0 or (len(args.py) > 0 and args.py in ("both", "all")):
        pythons = ["2.7", "3.6"]
    logger.info("python versions " + str( args.py))

    for python_version in pythons:
        if not args.skip_conda:
            package_name = args.project_name
            if package_name is None:
                package_name = "."
            conda_build_and_upload(
                python_version,
                args.channel,
                package_name=package_name,
                skip_upload=args.skip_upload
            )


def pypi_build_and_upload(args):
    pypi_upload = True
    if args.skip_pypi:
        pypi_upload = False

    if pypi_upload:
        logger.info("pypi upload")
        # preregistration is no longer required
        # mycall(["python", "setup.py", "register", "-r", "pypi"])
        if args.skip_upload:
            cmd = ["python", "setup.py", "sdist"]
        else:
            cmd = ["python", "setup.py", "sdist", "upload", "-r", "pypi"]
        mycall(cmd)

    # build conda and upload
    logger.debug("conda clean")

    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

    # this fixes upload confilct
    dr = glob.glob("dist/*.tar.gz")
    for onefile in dr:
        os.remove(onefile)

def check_meta_yaml_for_noarch(fn:Path):
    import re
    with open(fn, "rt") as fl:
        text = fl.read()

    mo = re.match(r"\n\s*noarch_python:\s*True", text)
    if mo:
        logger.info("Detected conda noarch python")
    return mo

def conda_build_and_upload(python_version, channels, package_name=None, skip_upload=False):
    if package_name is None:
        if op.exists("conda-recipe/meta.yaml"):
            package_name = "./conda-recipe/"
        else:
            package_name = "."

    fn_meta = Path(package_name) / "meta.yaml"
    noarch = check_meta_yaml_for_noarch(fn_meta)

    logger.debug("conda build")
    logger.debug("build python_version :" + str( python_version))
    python_short_version = python_version[0] + python_version[2]

    # subprocess.call("conda build -c mjirik -c SimpleITK .", shell=True)
    # if python_version == "noarch":
    if noarch:
        conda_build_command = ["conda", "build", package_name]
    else:
        conda_build_command = ["conda", "build", "--py", python_version,  package_name]
    for channel in channels:
        conda_build_command.append("-c")
        conda_build_command.append(channel[0])
    # if python_version == "noarch":
    if noarch:
        if skip_upload:
            conda_build_command.append("--no-anaconda-upload")
        skip_upload = True
    else:
        # upload in the end
        conda_build_command.append("--no-anaconda-upload")

    mycall(conda_build_command, ignore_error=False)
    conda_build_command.append("--output")
    # output_name_lines = subprocess.check_output(["conda", "build", "--python", python_version, "--output", "."])
    logger.debug(" ".join(conda_build_command))
    output_name_lines = subprocess.check_output(conda_build_command).decode()
    # get last line of output
    output_name = output_name_lines.split("\n")[-2]
    logger.debug("build output file: " + output_name)
    cmd_convert = ["conda", "convert", "-p", "all", output_name]
    if not noarch: # python_version != "noarch":
        logger.debug(" ".join(cmd_convert))
        mycall(cmd_convert)

    if package_name == ".":
        package_name = ""

    if skip_upload:
        logger.info("skip upload conda")
    else:
        logger.debug("binstar upload")
        # it could be ".tar.gz" or ".tar.bz2"
        mycall("anaconda upload */*" + package_name + "*" + python_short_version + "*.tar.*z*")
        mycall(["anaconda", "upload", output_name])

    logger.debug("rm files")
    dr = glob.glob("win-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("linux-*")
    for onedir in dr:
        shutil.rmtree(onedir)
    dr = glob.glob("osx-*")
    for onedir in dr:
        shutil.rmtree(onedir)

def init(args):
    import click
    import git
    project_name = click.prompt("Project name: ", default=args.project_name, type=str)

    globalconfig = git.GitConfigParser([os.path.normpath(os.path.expanduser("~/.gitconfig"))], read_only=True)
    git_user_name = globalconfig.get_value("user", "name")
    git_user_email = globalconfig.get_value("user", "email")


    githublogin = click.prompt("GitHub login: ", type=str)
    author = click.prompt("Author: ", default=git_user_name, type=str)
    email = click.prompt("Email: ", default=git_user_email, type=str)
    description = click.prompt("Project description: ", default="", type=str)
    license_str = click.prompt("License: ", default="MIT", type=str)
    make_init(
        project_name, author=author, email=email, license=license_str, githublogin=githublogin,
        description=description, dry_run=args.dry_run
    )

    pass


def create_file(fn:Path, content, interactive=True):
    import click
    if not op.exists(fn) or click.confirm(f"Rewrite file '{str(fn)}'?"):
        fn.parents[0].mkdir(parents=True, exist_ok=True)
        with open(fn, 'w') as the_file:
            the_file.write(content)


def make_init(project_name:str, author:str, email:str, license:str,
              githublogin:str, description:str,
              dry_run:bool):
    conda_recipe_path = Path("conda-recipe/")

    project_name = project_name
    fmt = dict(
        name=project_name,
        description=description,
        keywords="",
        author=author,
        email=email,
        githublogin=githublogin,
        license=license
    )
    formated_setup = file_content._SETUP_PY.format(**fmt)
    formated_travis = file_content._TRAVIS_YML.format(**fmt)
    formated_meta = file_content._META_YML.format(**fmt)
    if dry_run:
        print(formated_setup)
        print(formated_travis)
        print(formated_meta)
    else:

        create_file(Path(".condarc"), 'channels:\n  - default\n#  - mjirik')
        create_file(Path("setup.py"), formated_setup)
        create_file(Path("setup.cfg"), file_content._SETUP_CFG)
        create_file(conda_recipe_path / "meta.yaml", formated_meta)
        create_file(Path(".travis.yml"), formated_travis)
        create_file(Path(f"tests/{project_name}_test.py"), file_content._TESTS_MAIN_PY)
        create_file(Path("README.md"), file_content.README_MD.format(**fmt))

        # if not op.exists(".condarc"):
        #     with open('.condarc', 'a') as the_file:
        #         the_file.write('channels:\n  - default\n#  - mjirik')
        # if not op.exists("setup.py"):
        #     with open('setup.py', 'a') as the_file:
        #         the_file.write(formated_setup)
        # if not op.exists("setup.cfg"):
        #     with open('setup.cfg', 'a') as the_file:
        #         the_file.write(file_content._SETUP_CFG)
        # if not op.exists(conda_recipe_path / "meta.yaml"):
        #     with open(conda_recipe_path / 'meta.yaml', 'a') as the_file:
        #         the_file.write(formated_meta)
        # if not op.exists(".travis.yml"):
        #     with open('.travis.yml', 'a') as the_file:
        #         the_file.write(formated_travis)


def main():
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    logger.addHandler(ch)

    # create file handler which logs even debug messages
    # fh = logging.FileHandler('log.txt')
    # fh.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    # logger.addHandler(fh)
    # logger.debug('start')

    # input parser
    parser = argparse.ArgumentParser(
        description=__doc__
    )
    parser.add_argument(
        "action",
        help="Available values are: 'init', 'stay', 'patch', 'minor', 'major' or 'stable'. "
            "Git pull is performed in the beginning. "
            "If 'init' is used the project directory with all necessary files is prepared and app quits. "
            "Version number will be increased with bumpversion if option 'patch', 'minor' and 'major' is used. "
            "Command 'stay' causes skipping of the bumpversion. Comands 'stay', 'patch', 'minor' and 'major' "
            "build PyPi and conda package and upload it to the server. The changes are then pushed to git."
        ,
        default=None)
    parser.add_argument(
        "project_name",
        nargs='?',
        help="project directory (with setup.py) or new project name if 'init' action is used",
        default="default_project")
    parser.add_argument("--py",
            # default="2.7",
            # default="both",
            action="append",
            default=[],
            # default="all",
            help="specify python version. '--py 2.7' or '--py both' for python 3.6 and 2.7. "
                 "Parameter can be used multiple times.")
    parser.add_argument(
        "-c", "--channel",
        nargs=1,
        action="append",
        help="Add conda channel. Can be used multiple times.",
        default=[])
    parser.add_argument(
        "-V", "--version", action='store_true',
        help="Print version number",
        default=False)
    # parser.add_argument(
    #     "arg2",
    #     required=False,
    #     default=None)
    # parser.add_argument(
    #     '-i', '--inputfile',
    #     default=None,
    #     # required=True,
    #     help='input file'
    # )
    parser.add_argument(
        '-ll', '--loglevel', type=int, default=None,
        help='Debug level 0 to 100')

    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Debug mode')
    parser.add_argument(
        '-sg', '--skip-git', action='store_true',
        help='Skip git pull on beginning and git push after bumpversion.')
    parser.add_argument(
        '-sp', '--skip-pypi', action='store_true',
        help='Do not upload to pypi')
    parser.add_argument(
        '-sc', '--skip-conda', action='store_true',
        help='Do not process conda package')
    parser.add_argument(
        '-sb', '--skip-bumpversion', action='store_true',
        help='Do not build and upload pypi package')
    parser.add_argument(
        '-su', '--skip-upload', action='store_true',
        help='Do not upload to pypi and conda')
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Do not create any files in init')
    args = parser.parse_args()


    if args.loglevel is not None:
        ch.setLevel(args.loglevel)

    if args.debug:
        ch.setLevel(logging.DEBUG)

    if args.version:
        print(__version__)

    # print(dir(args))
    make(args)


if __name__ == "__main__":
    main()


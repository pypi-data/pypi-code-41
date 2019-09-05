import os
import re
import click

from aos.constant import *
from aos.managers.comp import CompManager
from aos.util import update_config_in
import ConfigParser

def validate_boards(ctx, param, value):
    return value

@click.command("init", short_help="Initialize AOS project")
@click.option("-d", "--project-dir", default=os.getcwd, help="Directory for initializing AOS project",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True))
@click.option("-b", "--board", multiple=True, metavar="BOARD", callback=validate_boards, help="Board component to install")
@click.option("-c", "--component", multiple=True, metavar="COMPONENT_LIST", help="Other component to inistall (eg. App, Middleware ...)")
@click.option("-a", "--all", is_flag=True, help="Install all available components")
@click.option("-s", "--silent", is_flag=True, help="Suppress progress reporting")
@click.option("-t", "--check-available", is_flag=True, help="Check if component available before installation")
@click.option("-u", "--baseurl", metavar="URL", help="Base URL of AliOS Things release repo")
@click.pass_context
def cli(ctx, project_dir, board, component, all, silent, check_available, baseurl):
    if not silent:
        click.echo("\nInitialize AliOS Things Project in %s" % \
            click.style(os.path.join(project_dir, OS_NAME), fg="cyan"))

    init_project_dir(project_dir)
    yumconf = os.path.join(project_dir, ".aos", "yum.conf")
    if os.path.isfile(yumconf):
        os.remove(yumconf)

    complist = []
    cm = CompManager(baseurl)
    cm.clean()
    if all:
        remote = True
        opts = []
        output, err = cm.list(remote, *opts)
        patten = re.compile(r"(.*)\.noarch\s*(.*\.aos)\s*")
        for line in output.splitlines():
            match = patten.match(line)
            if match:
                compname = "%s-%s" % (match.group(1), match.group(2))
                complist += [compname]

    if board:
        complist += board
    if component:
        complist += component

    if complist:
        if "board_" in " ".join(complist):
            cm.install(complist + OS_DEF_COMPS, check_available)
        else:
            cm.install(complist, check_available)

    os.chdir(os.path.join(project_dir, OS_NAME))
    update_config_in()

def init_project_dir(project_dir):
    if not os.path.isdir(project_dir):
        os.makedirs(project_dir)

    dot_aos = os.path.join(project_dir, ".aos")
    if not os.path.isdir(dot_aos):
        os.makedirs(dot_aos)

    source_dir = os.path.join(project_dir, OS_NAME)
    if not os.path.isdir(source_dir):
        os.makedirs(source_dir)

    download_dir = os.path.join(dot_aos, "downloads")
    if not os.path.isdir(download_dir):
        os.makedirs(download_dir)

    cf = ConfigParser.ConfigParser()
    cf.add_section("global")
    cf.set("global", "project_dir", project_dir)

    config_file = os.path.join(dot_aos, OS_CONFIG)
    cf.write(open(config_file, "w"))

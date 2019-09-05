import os
import click

from aos.util import cd_aos_root, error, popen
from aos.constant import GEN_SAL_STAGING, GEN_NEWPROJECT


@click.group(short_help="Create project or component")
@click.pass_context
def cli(ctx):
    pass

# Create sal driver from template
@cli.command("saldriver", short_help="Create SAL driver from template")
@click.argument("drivername", metavar="[DRIVERNAME]")
@click.option("-m", "--mfname", help="The manufacturer of device")
@click.option("-t", "--devicetype", required=True,
              type=click.Choice(["gprs", "wifi", "lte"]), help="The type of device")
@click.option("-a", "--author", help="The author of driver")
def create_sal_driver(drivername, mfname, devicetype, author):
    """ Create SAL driver staging code from template """

    args = [drivername]
    if mfname:
        args += ["-m%s" % mfname]
    if devicetype:
        args += ["-t%s" % devicetype]
    if author:
        args += ["-a%s" % author]

    # Get aos source root directory
    ret, original_dir = cd_aos_root()
    if ret != 'success':
        error("not in AliOS-Things source code directory")

    source_root = os.getcwd()
    if os.path.isdir(original_dir):
        os.chdir(original_dir)

    # Run script GEN_SAL_STAGING
    gen_sal_staging = "%s/%s" % (source_root, GEN_SAL_STAGING)
    if os.path.isfile(gen_sal_staging):
        cmd = ["python", gen_sal_staging] + list(args)
        popen(cmd)
    else:
        error("No %s found for current release!" % gen_sal_staging)

# Create project
@cli.command("project", short_help="Create user project")
@click.argument("projectname", metavar="[PROJECTNAME]")
@click.option("-b", "--board", required=True, help="Board for creating project")
@click.option("-d", "--projectdir", required=True, help="The project directory")
def create_project(projectname, board, projectdir):
    """ Create new project from template """
    args = [projectname]
    if board:
        args += ["-b%s" % board]
    if projectdir:
        args += ["-d%s" % projectdir]

    if "AOS_SDK_PATH" not in os.environ:
        error("No AliOS SDK installed")
    else:
        aos_sdk_path = os.environ["AOS_SDK_PATH"]

    gen_newproject = "%s/%s" % (aos_sdk_path, GEN_NEWPROJECT)
    if os.path.isfile(gen_newproject):
        cmd = ["python", gen_newproject] + list(args)
        popen(cmd)
    else:
        error("No %s found for current release!" % gen_newproject)

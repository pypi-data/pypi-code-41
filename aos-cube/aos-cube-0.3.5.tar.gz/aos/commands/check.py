import os, sys
import click

from aos.util import cd_aos_root, error, popen
from aos.constant import CHECK_WRAPPER

# Make command
@click.command("check", short_help="Call various check scripts, depends on what check implemented by current release ...")
@click.argument("args", required=False, nargs=-1, metavar="[ARGS...]")
def cli(args):
    """ Call various check functions implemented in OS.

        Show more ARGS with: $ aos check help
    """

    # Get aos source root directory
    ret, original_dir = cd_aos_root()
    if ret != 'success':
        error("not in AliOS-Things source code directory")

    source_root = os.getcwd()
    if os.path.isdir(original_dir):
        os.chdir(original_dir)

    # Run check scripts
    check_wrapper = "%s/%s" % (source_root, CHECK_WRAPPER)
    if os.path.isfile(check_wrapper):
        cmd = ["python", check_wrapper] + list(args)
        popen(cmd)
    else:
        error("No check scripts found for current release!")

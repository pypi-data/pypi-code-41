import os, sys
import click
from aos.util import log, error, popen, get_config_value
from aos.config import *
from aos.commands.upload import _call_scons_target

# Make command
@click.command("debug", short_help="Start gdb server")
@click.argument("target", required=False, nargs=-1)
@click.option("--work-path", "-w", help="Alternative work path if aos_sdk_path unavailable")
@click.option("--binaries-dir", "-b", help="Directory to store debug binaries")
@click.option("--start-client", "-c", is_flag=True, help="Start gdb client")
@click.option("--gdb-args", "-g", help="Arguments pass to gdb client")
def cli(target, work_path, binaries_dir, start_client, gdb_args):
    """ Initialize debug env for aos image. """
    from aos import __version__
    log('aos-cube version: %s\n' % __version__)

    debug_target = ' '.join(target)

    if work_path:
        if os.path.isdir(work_path):
            aos_path = work_path
        else:
            error("Can't find dir %s" % work_path)
    else:
        #cd to aos root_dir
        ret, original_dir = cd_aos_root()
        if ret != 'success':
            log("[INFO]: Not in AliOS-Things source code directory")
            log("[INFO]: Current directory is: '%s'\n" % original_dir)
            if os.path.isdir(original_dir):
                os.chdir(original_dir)

            aos_path = Global().get_cfg(AOS_SDK_PATH)
            if aos_path == None:
                error("[ERRO]: Not in aos_sdk_path, aos_sdk unavailable as well!")
            else:
                log("[INFO]: Config Loading OK, use '%s' as sdk path\n" % aos_path)
        else:
            aos_path = os.getcwd()
            log("[INFO]: Currently in aos_sdk_path: '%s'\n" % os.getcwd())

    # read app & board from .config
    if debug_target == '':
        # check AliOS Things version
        if os.path.exists(os.path.join(aos_path, 'build', 'Config.in')) == False:
            error('Target invalid')

        board = None
        app = None
        log("[INFO]: Not set target, read target from .config\n")

        config_file = os.path.join(aos_path, '.config')
        if os.path.exists(config_file) == False:
            error('Config file NOT EXIST: %s\n' % config_file)

        board = get_config_value('AOS_BUILD_BOARD', config_file)
        app = get_config_value('AOS_BUILD_APP', config_file)

        if not app and not board:
            error('None target in %s\n' % config_file)
        debug_target = '%s@%s' % (app, board)

    elif '@' not in debug_target or len(debug_target.split('@')) != 2:
        error('Target invalid')

    if work_path and not os.path.isdir(work_path):
        error("Can't find dir %s" % work_path)

    if binaries_dir and not os.path.isdir(binaries_dir):
        error("Can't find dir %s" % binaries_dir)

    extra_args = []
    if work_path and os.path.isdir(work_path):
        extra_args += ['WORKPATH=' + work_path]

    if binaries_dir and os.path.isdir(binaries_dir):
        extra_args += ['BINDIR=' + binaries_dir]

    if start_client:
        extra_args += ['STARTCLIENT=True']

    if gdb_args:
        extra_args += ['GDBARGS="' + gdb_args + '"']

    click.secho("[INFO]: Target: %s\n" % debug_target, fg="green")
    _call_scons_target(debug_target, 'debug', aos_path, extra_args)

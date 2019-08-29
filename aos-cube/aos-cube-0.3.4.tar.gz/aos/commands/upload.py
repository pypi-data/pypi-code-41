import os, sys
import click

from aos.util import log, error, popen
from aos.config import *

# Make command
@click.command("upload", short_help="Upload aos image")
@click.argument("target", required=False, nargs=-1)
@click.option("--work-path", "-w", help="Alternative work path if aos_sdk_path is unavailable")
@click.option("--binaries-dir", "-b", help="Dir to store upload binaries")
def cli(target, work_path, binaries_dir):
    """ Upload aos image to target platform. """
    from aos import __version__
    log('aos-cube version: %s\n' % __version__)

    upload_target = ' '.join(target)

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
    if upload_target == '':
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
        upload_target = '%s@%s' % (app, board)

    elif '@' not in upload_target or len(upload_target.split('@')) != 2:
        error('Target invalid')
        return

    extra_args = []
    extra_args += ['WORKPATH=' + aos_path]

    if binaries_dir and not os.path.isdir(binaries_dir):
        error("Can't find dir %s" % binaries_dir)

    extra_args = []
    if work_path:
        extra_args += ['WORKPATH=' + work_path]
    if binaries_dir:
        extra_args += ['BINDIR=' + binaries_dir]

    click.secho("[INFO]: Target: %s\n" % upload_target, fg="green")
    _call_scons_target(upload_target, 'upload', aos_path, extra_args)

def _call_scons_target(target, command, aos_path, extra_args=None):
    """ Call scons to run specific command """
    sconscript = os.path.join(aos_path, 'ucube.py')
    if not os.path.exists(sconscript):
        sconscript = os.path.join(aos_path, 'build/ucube.py')

    make_args = ['scons -f ' + sconscript + ' COMMAND=' + command]

    target_find = False

    if '@' in target and not target_find:
        targets = target.split('@')
        if len(targets) < 2:
            error('Must special app and board when build aos')

        app = 'APPLICATION='+targets[0]
        board = 'BOARD=' + targets[1]
        make_args.append(app)
        make_args.append(board)

        if len(targets) == 3:
            build_type = 'TYPE=' + targets[2]
            make_args.append(build_type)

        target_find = True

    if extra_args:
        make_args += extra_args

    ret = popen(' '.join(make_args), shell=True, cwd=os.getcwd())

    return ret

import os, sys
import click

from aos.util import log, info, error, popen, Config, cd_aos_root, get_config_value
from aos.config import Global
from aos.constant import APP_CONFIG, AOS_SDK_PATH

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
        # upload from app project
        curr_dir = os.getcwd()
        config_file = os.path.join(curr_dir, APP_CONFIG)
        if os.path.isfile(config_file):
            ac = Config(config_file)
            aos_path = ac.get("AOS_SDK_PATH")
            work_path = curr_dir
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

        config_file = os.path.join(work_path if work_path else aos_path, '.config')
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

    if binaries_dir and not os.path.isdir(binaries_dir):
        error("Can't find dir %s" % binaries_dir)

    # for new board config
    if os.path.exists(os.path.join(aos_path, 'build', 'board_config', 'board_upload.py')):
        sys.path.append(os.path.join(aos_path, 'build', 'board_config'))
        try:
            from board_upload import aos_upload
        except Exception, err:
            info(err)
            info(Exception)
            error("Import board_upload.py: failed %s" % err)
    else:
        sys.path.append(os.path.join(aos_path, 'build', 'site_scons'))
        try:
            from scons_upload import aos_upload
        except Exception, err:
            info(err)
            info(Exception)
            error("Import scons_upload.py: failed %s" % err)

    click.secho("[INFO]: Target: %s" % upload_target, fg="green")
    aos_upload(upload_target, work_path, binaries_dir)
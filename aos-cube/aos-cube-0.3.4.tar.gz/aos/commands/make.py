import os, sys
import subprocess
import shutil
import traceback

import click
from aos.util import log, error, cd_aos_root, is_domestic, popen, get_board_dir
from aos.program import *

# Make command
@click.command("make", short_help="Make aos program/component")
@click.argument("targets", required=False, nargs=-1, metavar="[TARGETS...]")
@click.option("-c", "--cmd", metavar="[CMD]", help="Sub build stage for target")
def cli(targets, cmd):
    """ Make aos program/component """
    from aos import __version__
    log('aos-cube version: %s\n' % __version__)

    make_args = ' '.join(targets)
    for arg in targets:
        if '@' in arg:
            targets = arg.split('@')
            if len(targets) < 2:
                error('Must special app and board when build aos')

            board = targets[1]
            if cmd:
                make_args = re.sub(arg, "%s.%s" % (arg, cmd), make_args)

            if board in get_scons_enabled_boards():
                scons_build(targets)
            else:
                make_build(make_args)

            return
    #aos make clean go here
    make_build(make_args)

#
# Common functions
#
def download_toolchains(downloads):
    tmp_dir = 'tmp_{0:02x}'.format(ord(os.urandom(1)))
    while os.path.isdir(tmp_dir):
        tmp_dir = 'tmp_{0:02x}'.format(ord(os.urandom(1)))
    try:
        os.mkdir(tmp_dir)
    except:
        print('download toolchains failed: unable to create a temp folder')
        return
    try:
        os.chdir(tmp_dir)
        for download in downloads:
            result = 0
            name, git_url, dst_dir = download
            print('toolchain {} missing, start download ...'.format(name))
            print(git_url + ' -> ' + dst_dir)
            result += subprocess.call(['git', 'clone', '--depth=1', git_url, name])
            if result > 0:
                print('git clone toolchain {} failed'.format(name))
                print('You can mannually try fix this problem by running:')
                print('    git clone {} {}'.format(git_url, name))
                print('    mv {0}/main {1} && rm -rf {0}'.format(name, dst_dir))
            src_dir = name + '/main'
            if os.path.exists(src_dir) == False:
                print('toolchain folder {} none exist'.format(src_dir))
                result += 1
            if result == 0:
                dst_dir = '../' + dst_dir
                if os.path.isfile(dst_dir) == True:
                    os.remove(dst_dir)
                if os.path.isdir(dst_dir) == True:
                    shutil.rmtree(dst_dir)
                if os.path.isdir(os.path.dirname(dst_dir)) == False:
                    os.makedirs(os.path.dirname(dst_dir))
                shutil.move(src_dir, dst_dir)
                print('download toolchain {} succeed'.format(name))
            else:
                print('download toolchain {} failed'.format(name))
    except:
        traceback.print_exc()
    finally:
        os.chdir('../')
    try:
        shutil.rmtree(tmp_dir)
    except:
        print("toolchain auto-install error: can not remove temp folder {}, please remove it manually".format(tmp_dir))
        pass

def is_specific_path(toolchain):
    try:
        if toolchain['path_specific']:
            return True
    except KeyError as exc:
        return False
    return False

def _install_toolchains(build_args):
    board = None
    host_os = get_host_os()
    if host_os == None:
        error('Unsupported Operating System!')

    #cd to aos root_dir
    ret, original_dir = cd_aos_root()
    if ret != 'success':
        error("not in AliOS-Things source code directory")

    #check config file to be enable this function (for backward compatability)
    autodownload_enable = False
    if os.path.exists('build/toolchain_config.py'):
        sys.path.append("./build")
        try:
            from toolchain_config import auto_download
        except:
            error("Import toolchain configs failed")

        if auto_download == "yes":
            autodownload_enable = True
    elif os.path.exists('build/toolchain_autodownload.config'):
        try:
            with open('build/toolchain_autodownload.config') as file:
                if 'yes' in file.read(): autodownload_enable = True
        except:
            pass

    if autodownload_enable == False:
        if os.path.isdir(original_dir): os.chdir(original_dir)
        return

    for arg in build_args:
        if '@' not in arg:
            continue
        args = arg.split('@')
        board = args[1]
        break

    if not board:
        board = get_config_value("AOS_BUILD_BOARD")

    if not board:
        if os.path.isdir(original_dir):
            os.chdir(original_dir)
        return

    if not os.path.isdir(os.path.join('board', board)):
        board_dir = get_board_dir(board)
        if not board_dir:
            error('Can not find board {}'.format(board))

    downloads = []
    if os.path.exists('build/toolchain_config.py'):
        from toolchain_config import boards
    else:
        from aos.constant import boards

    if board in boards:
        print('Check if required tools for {} exist'.format(board))
        for toolchain in boards[board]:
            name = toolchain['name']
            command = toolchain['command']
            version = toolchain['version']
            if is_specific_path(toolchain) is True:
                cmd_path = '{}/bin/{}'.format(toolchain['path'], command)
            else:
                cmd_path = '{}/{}/bin/{}'.format(toolchain['path'], host_os, command)
            if cmd_version_match(cmd_path, version) == True:
                continue
            if toolchain['use_global'] and cmd_version_match(command, version) == True:
                continue
            git_url = toolchain['{}_url'.format(host_os)]
            if git_url == '':
                continue
            if is_domestic() is False:
                git_url = git_url.replace('gitee', 'github')
                git_url = git_url.replace('alios-things', 'aliosthings')

            if is_specific_path(toolchain) is True:
                downloads.append([name, git_url, '{}'.format(toolchain['path'])])
            else:
                downloads.append([name, git_url, '{}/{}'.format(toolchain['path'], host_os)])
    if len(downloads): download_toolchains(downloads)

    if os.path.isdir(original_dir): os.chdir(original_dir)

#
# Support for scons build
#
def scons_build(args):
    if os.path.exists('ucube.py') == True:
        make_args = ['scons -j4 -f ucube.py']
    else:
        make_args = ['scons -j4 -f build/ucube.py']

    target_find = False

    for arg in args:
        if '@' in arg and not target_find:
            targets = arg.split('@')
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
        elif arg.startswith('JOBS=') and arg.replace('JOBS=', '').isdigit() == True:
            jnum = arg.replace('JOBS=', '-j')
            make_args[0] = make_args[0].replace('-j4', jnum)
        else:
            make_args.append(arg)

    popen(' '.join(make_args), shell=True, cwd=os.getcwd())

def get_scons_enabled_boards():
    if os.path.exists("build/scons_enabled.py"):
        module_path = os.path.abspath(os.path.join('build'))
        sys.path.append(module_path)
        from scons_enabled import scons_enabled_boards
        return scons_enabled_boards
    else:
        return []

#
# Support for make build
#
def make_build(make_args):
    # aos new program
    if os.path.isfile(os.path.join(os.getcwd(), Cfg.file)):
        pd = Program(os.getcwd())
        os_path = pd.get_cfg(OS_PATH)

        build_dir = ''
        out_path = ''
        is_build_dir = 'BUILD_DIR=' in make_args or os.environ.get('BUILD_DIR')
        if not is_build_dir:
            out_path = os.path.join(os.getcwd(), 'out').replace(os.path.sep, '/')
            build_dir = 'BUILD_DIR=' + out_path

        # cube_makefile = 'CUBE_MAKEFILE=' + os.path.join(pd.get_cfg(PROGRAM_PATH), CUBE_MAKEFILE).replace(os.path.sep, '/')
        app_dir = 'APPDIR=' + os.path.dirname(os.getcwd())

        with cd(os_path):
            cube_modify = pd.get_cfg(CUBE_MODIFY)
            if cube_modify == '1':
                _run_make(['-e', '-f build/Makefile', 'clean'])
                if build_dir:
                    shutil.rmtree(out_path, True)
                pd.set_cfg(CUBE_MODIFY, '0')
            _run_make(['-e', '-f build/Makefile', make_args, app_dir, build_dir])
    else:
        # aos source code
        _run_make(['-e', '-f build/Makefile', make_args])

def _run_make(arg_list):
    #install dependent toolchains
    download_toolchain = "yes"
    target_no_toolchain = [".config", ".menuconfig", "clean", "distclean", "help", "export-keil", "export-iar", "_defconfig"]
    for arg in arg_list:
        for target in target_no_toolchain:
            if target in arg:
                download_toolchain = "no"
                break

    if download_toolchain == "yes":
        _install_toolchains(sys.argv[2:])

    # check operating system
    host_os = get_host_os()
    if host_os == None:
        error('Unsupported Operating System!')

    #cd to aos root_dir
    ret, original_dir = cd_aos_root()
    if ret != 'success':
        error("not in AliOS-Things source code directory")

    make_cmds = {
        'Win32': 'cmd/win32/make.exe',
        'Linux64': 'cmd/linux64/make',
        'Linux32': 'cmd/linux32/make',
        'OSX': 'cmd/osx/make'
        }
    tools_dir = os.path.join(os.getcwd(), 'build').replace('\\', '/')
    make_cmd = os.path.join(tools_dir, make_cmds[host_os])

    # Run make command
    make_cmd_str = ' '.join([make_cmd, 'HOST_OS=' + host_os, 'TOOLS_ROOT=' + tools_dir] + list(arg_list))
    popen(make_cmd_str, shell=True, cwd=os.getcwd())
    if os.path.isdir(original_dir): os.chdir(original_dir)

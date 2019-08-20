import sys
import argparse
import ConfigParser
from datetime import datetime
import os
import shutil
from os import path


def create_argument_object():
    this_path = path.dirname(path.realpath(__file__))
    usage_txt_path = path.join(
        this_path, 'resources/argument-object/usage.txt')
    description_txt_path = path.join(
        this_path, 'resources/argument-object/description.txt')
    epilog_txt_path = path.join(
        this_path, 'resources/argument-object/epilog.txt')

    parser = argparse.ArgumentParser(
        prog=None,
        usage=open(usage_txt_path).read(),
        description=open(description_txt_path).read(),
        epilog=open(epilog_txt_path).read(),
        parents=[],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prefix_chars='-',
        fromfile_prefix_chars=None,
        argument_default=None,
        conflict_handler='error',
        add_help=True)
    return parser


def add_argument_object(parser):

    parser.add_argument(
        '-i',
        action='count',
        help='prompt before removal (default)'
    )

    parser.add_argument(
        '-f', '--force',
        action='count',
        help='force delete without promt'
    )

    parser.add_argument(
        '-r', '-R', '--recursive',
        action='count',
        help='remove directories and their contents recursively'
    )

    parser.add_argument(
        '--no-backup',
        action='count',
        help='remove without backup mechanism (can not recover later)'
    )

    parser.add_argument(
        '--recover',
        action='count',
        help='recover file from trash'
    )

    parser.add_argument(
        '--list-trash',
        action='count',
        help='show list deleted file, sort by date time'
    )

    parser.add_argument(
        '--wipe-all',
        action='count',
        help='complete delete everything from recycle bin, free disk space'
    )

    parser.add_argument(
        '-v', '--version',
        action='count',
        help='show version information and exit'
    )

    parser.add_argument(
        'filename',
        action='store',
        nargs='*',
        help='directory or file you want to delete'
    )
    return parser


# get absolute path
def full_path(path_X):
    return path.abspath(path.expanduser(path_X))


# check path_X is subdir of path_Y or not
def check_is_subdir(path_X, path_Y):
    if path.commonprefix([path_X, path_Y]) == path_Y:
        return True
    return False


def check_is_hidden_name(name):
    temp = name.split('.')
    if not temp[0]:
        return True
    return False


def wipe_recycle_bin(recycle_path):
    for fname in os.listdir(recycle_path):
        file_path = path.join(recycle_path, fname)
        if path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)
    return


def parse_config_file():
    # parse config from file

    # check if user config exist or not
    if not path.exists(full_path('~/.config/btrm.conf')):
        this_path = path.dirname(path.realpath(__file__))
        config_path = full_path(path.join(this_path, 'config/btrm.conf'))
        shutil.copy(config_path, full_path('~/.config/btrm.conf'))

    config_path = full_path('~/.config/btrm.conf')
    config = ConfigParser.ConfigParser()
    config.read(config_path)

    # check if recycle bin exist or not, if not then generate new
    recycle_path = full_path(config.get('default', 'recyclebin_path'))
    if not os.path.isdir(recycle_path):
        os.mkdir(recycle_path)
        os.mkdir(recycle_path + '/trashs')
        os.mkdir(recycle_path + '/info')

    if not os.path.isdir(recycle_path + '/trashs'):
        os.mkdir(recycle_path + '/trashs')

    if not os.path.isdir(recycle_path + '/info'):
        os.mkdir(recycle_path + '/info')

    return config


def remove_file(arguments, config):
    # get all config info
    recycle_path = full_path(config.get('default', 'recyclebin_path'))

    # get list existed trash in recycle bin
    list_trashs = os.listdir(recycle_path + "/trashs/")

    for fname in arguments.filename:
        path_name = full_path(fname)  # recognize tidle(~) sign in unix

        # ------------------------- COMMON ERROR ------------------------------
        if not path.exists(path_name):      # path not exist
            print(("btrm: can not remove '{0}': no such "
                   "file or directory.").format(fname))
            continue

        if path.ismount(path_name):     # check is mountpoint
            print("btrm: can not remove '{0}'(mount point).".format(fname))
            continue

        if check_is_subdir(recycle_path, path_name):  # check subdir
            print("btrm: can not remove '{0}': "
                  "{1} is subdirectory of {0}."
                  .format(path_name, recycle_path))
            continue

        if path.isdir(path_name) and arguments.recursive is None:
            print(
                "btrm: cannot remove '{0}': Is a directory".format(path_name))
            continue

        if arguments.force is None:     # verify remove process
            char = str(raw_input(
                "do you want to remove '{0}' (y/n): ".format(path_name)))
            if char != 'y':
                continue

        # -------------------------------------------------------------------

        if arguments.no_backup:     # no backup, complete remove from disk
            if path.isdir(path_name):
                shutil.rmtree(path_name)
            else:
                os.remove(path_name)
            continue

        # prevent duplicate trash name in trash folder-----------------------
        temp = path.basename(path_name)
        base_file = temp
        count = 0
        hide = check_is_hidden_name(temp)
        while base_file in list_trashs:
            count = count + 1
            arr = temp.split('.')
            if hide is True:
                arr.insert(1, str(count))
            else:
                arr.insert(0, str(count))
            base_file = '.'.join(arr)

        # remove---------------------------------------------------------------
        os.renames(path_name, recycle_path + '/trashs/{0}'.format(base_file))

        # write info-----------------------------------------------------------
        current_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        form_trash_info = """[Trash Info]\nOldPath={0}\nDeletionDateTime={1}"""
        wfile = open(recycle_path +
                     '/info/{0}.trashinfo'.format(base_file), 'w')
        wfile.write(form_trash_info.format(path_name, current_time))

    return


def recover_file(arguments, config):
    # get all config info
    recycle_path = full_path(config.get('default', 'recyclebin_path'))

    # get list existed trash in recycle bin
    list_trashs = os.listdir(recycle_path + '/trashs/')

    for fname in arguments.filename:
        if fname not in list_trashs:
            print("btrm: can not recover '{0}': "
                  "file not in recycle bin".format(fname))
            continue

        trash_info_path = recycle_path + '/info/' + fname + '.trashinfo'
        trash_path = recycle_path + '/trashs/' + fname

        trash_info = ConfigParser.ConfigParser()
        trash_info.read(trash_info_path)
        old_path = trash_info.get('Trash Info', 'OldPath')

        if path.exists(old_path):       # check if path exists, warning
            char = str(raw_input("path '{0}' existing, "
                                 "allow overwrite? (y/n): ".format(old_path)))
            if char != 'y':
                continue
        os.renames(trash_path, old_path)
        os.remove(trash_info_path)
        if not path.exists(recycle_path + '/trashs/'):
            shutil.rmtree(recycle_path + '/info/')

    return


def process_arg(arguments, config):

    if arguments.version:   # show version then exit
        this_path = path.dirname(path.realpath(__file__))
        version_txt_path = path.join(
            this_path, 'resources/argument-object/version.txt')
        print(open(version_txt_path).read())
        return

    if arguments.list_trash:    # show all removed file
        os.system(
            "ls -hAlt --color=always {0} | sed -n '1!p'".format(full_path(
                config.get('default', 'recyclebin_path')) + '/trashs'))
        return

    if arguments.wipe_all:
        recycle_path = full_path(config.get('default', 'recyclebin_path'))
        wipe_recycle_bin(recycle_path)
        return

    if not arguments.filename:          # list file is empty
        print("btrm: missing operand\n"
              "Try 'btrm -h\--help' for more information.")
        return

    if arguments.recover:   # user want to recover file
        recover_file(arguments, config)
    else:                               # user want to delete file
        remove_file(arguments, config)

    return


def main():
    parser = create_argument_object()
    parser = add_argument_object(parser)
    namespace_arguments = parser.parse_args()

    config = parse_config_file()
    process_arg(namespace_arguments, config)
    return


if __name__ == '__main__':
    main()

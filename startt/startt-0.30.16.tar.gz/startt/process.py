import os
import glob
from shutil import copyfile
from startt.analyze import get_template_name
from startt import config


def copy_template(filename, template_folder):
    template_name = os.path.join(template_folder,
                                 get_template_name(filename))
    correct_filename = get_filename(filename)
    if os.path.isfile(template_name):
        copy_file_template(template_name, correct_filename)
    elif os.path.isdir(template_name):
        copy_directory_template(template_name, correct_filename)
    else:
        print('Doing nothing')


def get_filename(filename):
    folder, basename = os.path.split(filename)
    segments = basename.split('.')
    return os.path.join(folder, '.'.join([segments[0], segments[-1]]))


def copy_file_template(template_name, target_name):
    copyfile(template_name, target_name)


def copy_directory_template(template_name, target_name):
    filenames = glob.glob(os.path.join(template_name, '*'))
    cfgname = os.path.join(template_name, 'config.json')
    if cfgname in filenames:
        filenames.pop(filenames.index(cfgname))

    cfg = config.config(template_name)
    for fname in filenames:
        base = os.path.basename(fname)
        if base.lower().startswith('main'):
            copyfile(fname, target_name)
        else:
            operation = cfg.get(fname, cfg['default'])
            if operation == 'link':
                os.symlink(fname, base)
            elif operation == 'copy':
                copyfile(fname, base)

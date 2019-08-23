import os
import glob


def get_template_folder(args):
    return os.path.expanduser(args['--template-folder'])


def get_available_templates(template_folder):
    return glob.glob(os.path.join(template_folder, '*'))


def get_template_name(fname):
    basename = os.path.basename(fname)
    segments = basename.split('.')[1:]
    if len(segments) == 1:
        segments.insert(0, 'default')
    return '.'.join(segments)

import os
import sys
import inspect

def add_sys_path(target_rel_path):
    '''
    Add the given path (relative to the caller's file path) to sys.path
    It's a sys.path hack for importing modules using relative paths
    https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time

    :param target_rel_path: target path (relative to the caller's file path)
    '''
    rel_folder = os.path.normpath(target_rel_path)

    # find caller's file path
    previous_frame = inspect.currentframe().f_back
    cmd_folder = os.path.realpath(os.path.dirname(inspect.getfile(previous_frame)))
    cmd_subfolder = os.path.join(cmd_folder, rel_folder)

    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)

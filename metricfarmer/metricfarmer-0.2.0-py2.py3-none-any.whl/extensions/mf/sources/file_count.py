import glob
import os


def source_file_count(**kwargs):
    path = kwargs.get('path', os.getcwd())
    pattern = kwargs.get('pattern', '**/*')

    file_list = glob.glob(path + '/' + pattern, recursive=True)
    return len(file_list)

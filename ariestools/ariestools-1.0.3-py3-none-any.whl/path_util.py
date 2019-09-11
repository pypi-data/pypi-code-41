import platform, os


def replace_sys_path(path: str):
    """
    转windows路径分隔符
    :param path:
    :return:
    """
    if "windows" in platform.system().lower():
        return path.replace("/", os.sep)
    else:
        return path


def get_path_by_relative(relative_path: str):
    """
    根据相对路径，获取绝对路径
    :param relative_path:
    :return:
    """
    return os.path.realpath('') + replace_sys_path(relative_path)

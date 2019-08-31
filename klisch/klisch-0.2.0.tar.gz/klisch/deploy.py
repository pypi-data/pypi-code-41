import pathlib
import shutil
import uuid


def codepack(paths, output='output'):
    dest_folder = pathlib.Path(output)
    dest_folder.mkdir(exist_ok=True, parents=True)

    for path in paths:
        path = pathlib.Path(path)
        if path.is_dir():
            if path.is_absolute():
                sub_folder = path.stem
            else:
                rel_path_clipped = str(path).replace('..\\', '')
                sub_folder = pathlib.Path(rel_path_clipped)
            copy_folder(path, dest_folder / sub_folder)
        elif path.is_file():
            copy(path, dest_folder)


def generate_uuid(segment: int = 0):
    uid = uuid.uuid1().hex
    if segment:
        uid = uid[:segment]
    return uid


def copy_folder(src_path, dst_path):
    """Copy folder to specific destination.

    Args:
        src_path (str or :class:`pathlib.Path`): source file path.
        dst_path (str or :class:`pathlib.Path`): destination file path.
    """
    src_path = str(src_path)
    dst_path = str(dst_path)
    try:
        shutil.copytree(src_path, dst_path)
    except (shutil.Error, OSError) as e:
        print('Directory not copied. Error: %s' % e)


def copy(src_path, dst_path):
    """Copy file to specific destination.

    Args:
        src_path (str or :class:`pathlib.Path`): source file path.
        dst_path (str or :class:`pathlib.Path`): destination file path.
    """
    src_path = str(src_path)
    dst_path = str(dst_path)
    return shutil.copy(src_path, dst_path)

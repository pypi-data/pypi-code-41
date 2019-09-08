import pathlib
import uuid
import warnings

from klisch import files
from klisch.files import Path
from klisch.utils import color_print


def codepack(paths, output='output'):
    warnings.simplefilter('default')
    warnings.warn('codepack will be deprecated, use pack_folder instead', DeprecationWarning)
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
            files.copy_folder(path, dest_folder / sub_folder)
        elif path.is_file():
            files.copy(path, dest_folder)


def pack_folder(
    folder_path: Path, output: Path = 'output',
    exist_ok: bool = True, dry_run: bool = False, verbose: bool = False
):
    src_folder = pathlib.Path(folder_path)
    dest_folder = pathlib.Path(output)
    dest_folder.mkdir(exist_ok=True, parents=True)

    def discovery(subpath: pathlib.Path):
        rel_path = subpath.relative_to(src_folder)
        dst_path = dest_folder / rel_path

        if subpath.is_symlink():
            sym_link = subpath.resolve()
            if dry_run or verbose:
                color_print(f'Symlink {sym_link} <- {dst_path}', color='magenta')
            if exist_ok and dst_path.exists():
                return
            if not dry_run:
                files.ensure_parent_folder_exists(dst_path)
                dst_path.symlink_to(sym_link)
        elif subpath.is_file():
            if dry_run or verbose:
                color_print(f'Copy {subpath} -> {dst_path}', color='white')
            if not dry_run:
                files.copy(subpath, dst_path)
        elif subpath.is_dir():
            for entry in subpath.glob('*'):
                discovery(entry)

    discovery(src_folder)


def generate_uuid(segment: int = 0):
    uid = uuid.uuid1().hex
    if segment:
        uid = uid[:segment]
    return uid

import fnmatch
import glob
import logging
import os
from io import StringIO
from time import sleep
from typing import TextIO, Iterator, Tuple, Collection, Dict, Set, Sequence

import jinja2
import markdown as md
from watchdog import observers, events

from .extensions import CoreExtension


class DndMarkdown:
    def __init__(self, template: jinja2.Template) -> None:
        self._template = template

    def convert(self, markdown_file: TextIO, output_file: TextIO) -> None:
        Converter(self._template).convert(markdown_file, output_file)

    def convert_all(self, md_root: str, html_root: str) -> None:
        MultiConverter(Converter(self._template), FileManager(md_root, html_root)).convert_all()

    def watch(self, md_root: str, html_root: str) -> None:
        Observer(Converter(self._template), md_root, html_root).watch()

    def generate_indices(self, md_root: str, html_root: str, template: jinja2.Template = None) -> None:
        if template is None:
            template = self._template
        IndexGenerator(FileManager(md_root, html_root), Converter(template)).generate_indexes()


FILE_CREATED = 'file{} created'
FILE_REMOVED = 'file{} removed'
FILE_UPDATED = 'file{} updated'
DIR_CREATED = 'dir{} created'
DIR_REMOVED = 'dir{} removed'

CHANGE_TYPES = [FILE_REMOVED, DIR_REMOVED, DIR_CREATED, FILE_CREATED, FILE_UPDATED]


class FileChangeResult:
    def __init__(self, changes: Dict[str, str] = None, created_files: Collection[str] = None,
                 removed_files: Collection[str] = None, updated_files: Collection[str] = None,
                 created_dirs: Collection[str] = None, removed_dirs: Collection[str] = None) -> None:
        self._changes = changes if changes is not None else {}
        if created_files is not None:
            self._changes.update(dict(zip(created_files, [FILE_CREATED] * len(created_files))))
        if removed_files is not None:
            self._changes.update(dict(zip(removed_files, [FILE_REMOVED] * len(removed_files))))
        if updated_files is not None:
            self._changes.update(dict(zip(updated_files, [FILE_UPDATED] * len(updated_files))))
        if created_dirs is not None:
            self._changes.update(dict(zip(created_dirs, [DIR_CREATED] * len(created_dirs))))
        if removed_dirs is not None:
            self._changes.update(dict(zip(removed_dirs, [DIR_REMOVED] * len(removed_dirs))))

    def __add__(self, other: 'FileChangeResult') -> 'FileChangeResult':
        self_changes = self.partition_changes_by_type()
        other_changes = other.partition_changes_by_type()

        created_files = (self_changes[FILE_CREATED] | other_changes[FILE_CREATED])
        removed_files = (self_changes[FILE_REMOVED] | other_changes[FILE_REMOVED])
        updated_files = self_changes[FILE_UPDATED] | other_changes[FILE_UPDATED] | (created_files & removed_files)
        created_files -= updated_files
        removed_files -= updated_files

        created_dirs = (self_changes[DIR_CREATED] | other_changes[DIR_CREATED])
        removed_dirs = (self_changes[DIR_REMOVED] | other_changes[DIR_REMOVED])
        updated_dirs = created_dirs & removed_dirs
        created_dirs -= updated_dirs
        removed_dirs -= updated_dirs

        return FileChangeResult(
            created_files=created_files, removed_files=removed_files, updated_files=updated_files,
            created_dirs=created_dirs, removed_dirs=removed_dirs
        )

    def __iter__(self) -> Iterator[Tuple[str, int, str]]:
        for change, paths in filter(lambda c: len(c[1]) > 0, self.partition_changes_by_type().items()):
            yield len(paths), change.format('' if len(paths) == 1 else 's')

    def __str__(self) -> str:
        if len(self._changes) == 1:
            path, change = next(iter(self._changes.items()))
            return '{}: {}'.format(change.format('').capitalize(), path)
        return ', '.join(['{} {}'.format(num, type_) for num, type_ in self])

    def get_type(self, change: str) -> Set[str]:
        return set([file for file, file_change in self._changes.items() if file_change == change])

    def partition_changes_by_type(self) -> Dict[str, Set[str]]:
        files_by_change = {}
        for change in CHANGE_TYPES:
            files_by_change[change] = self.get_type(change)
        return files_by_change


class CreatedFile(FileChangeResult):
    def __init__(self, path: str) -> None:
        super().__init__(created_files=[path])


class RemovedFile(FileChangeResult):
    def __init__(self, path: str) -> None:
        super().__init__(removed_files=[path])


class UpdatedFile(FileChangeResult):
    def __init__(self, path: str) -> None:
        super().__init__(updated_files=[path])


class CreatedDir(FileChangeResult):
    def __init__(self, path: str) -> None:
        super().__init__(created_dirs=[path])


class RemovedDir(FileChangeResult):
    def __init__(self, path: str) -> None:
        super().__init__(removed_dirs=[path])


class FileManager:
    def __init__(self, md_root: str, html_root: str) -> None:
        super().__init__()
        self._md_root = os.path.abspath(md_root)
        self._html_root = os.path.abspath(html_root)

        self._md_glob_pattern = os.path.join(self._md_root, '**/*.md')
        self._html_glob_pattern = os.path.join(self._html_root, '**/*.html')
        self._assets_glob_pattern = os.path.join(self._html_root, 'assets/**/*')

        self._md_fnmatch_pattern = os.path.join(self._md_root, '*.md')
        self._html_fnmatch_pattern = os.path.join(self._html_root, '*.html')

    def join_md_path(self, dir_, base, must_exist: bool = False) -> str:
        path = os.path.join(dir_, base)
        if not self.is_md(path, must_exist):
            raise ValueError
        return path

    def join_html_path(self, dir_, base, must_exist: bool = False) -> str:
        path = os.path.normpath(os.path.join(dir_, base))
        if not self.is_html(path, must_exist):
            raise ValueError
        return path

    def get_all_md_paths(self) -> Sequence[str]:
        paths = glob.glob(self._md_glob_pattern, recursive=True)
        return sorted([os.path.abspath(path) for path in paths])

    def get_all_md_dirs(self) -> Sequence[Tuple[str, str]]:
        dirs = set()
        for dir_ in map(os.path.dirname, self.get_all_md_paths()):
            while len(dir_) >= len(self._md_root):
                dirs.add(dir_)
                dir_ = os.path.dirname(dir_)
        return [(dir_, os.path.basename(dir_)) for dir_ in sorted(dirs)]

    def get_entries_in_md_dir(self, dir_: str) -> Sequence[str]:
        entries = [os.path.splitext(os.path.basename(path))[0]
                   for path in self.get_all_md_paths()
                   if os.path.dirname(path) == dir_]
        entries.extend([basename for path, basename in self.get_all_md_dirs() if os.path.dirname(path) == dir_])
        return entries

    def get_all_html_paths(self) -> Sequence[str]:
        paths = set(glob.glob(self._html_glob_pattern, recursive=True))
        paths.difference_update(glob.glob(self._assets_glob_pattern, recursive=True))
        return sorted([os.path.abspath(path) for path in paths])

    def get_html_path_from_md_path(self, md_path: str, md_must_exist: bool = False,
                                   html_must_exist: bool = False) -> str:
        if not self.is_md(md_path, md_must_exist):
            raise ValueError

        md_dir, md_base = os.path.split(md_path)
        rel_dir = os.path.relpath(md_dir, self._md_root)
        html_base = md_base[:-3] + '.html'
        html_dir = os.path.join(self._html_root, rel_dir)

        return self.join_html_path(html_dir, html_base, html_must_exist)

    def make_directory_and_ancestors(self, path: str, is_file: bool = True) -> FileChangeResult:
        path = os.path.normpath(path)

        if os.path.exists(path):
            return FileChangeResult()

        result = self.make_directory_and_ancestors(os.path.dirname(path), False)
        if not is_file:
            os.mkdir(path)
            dir_result = CreatedDir(path)
            logging.debug(dir_result)
            result += dir_result
        return result

    def is_md(self, path: str, must_exist: bool = True) -> bool:
        path = os.path.abspath(path)
        return fnmatch.fnmatch(path, self._md_fnmatch_pattern) and (not must_exist or os.path.isfile(path))

    def is_html(self, path: str, must_exist: bool = True) -> bool:
        path = os.path.abspath(path)
        return fnmatch.fnmatch(path, self._html_fnmatch_pattern) and (not must_exist or os.path.isfile(path))

    def dir_has_md(self, dir_path: str, md_name: str) -> bool:
        return self.is_md(os.path.join(dir_path, md_name))

    def remove_html(self, path) -> FileChangeResult:
        if not self.is_html(path):
            raise ValueError
        os.remove(path)
        result = RemovedFile(path)
        logging.debug(result)
        return result

    def remove_all_html(self) -> FileChangeResult:
        result = FileChangeResult()
        for html_path in self.get_all_html_paths():
            result += self.remove_html(html_path)
            result += self.remove_empty_in_html_path(html_path)
        return result

    def remove_empty_in_html_path(self, path: str) -> FileChangeResult:
        if os.path.commonprefix([path, self._html_root]) != self._html_root:
            raise ValueError
        result = FileChangeResult()
        if os.path.exists(path):
            try:
                os.rmdir(path)
                dir_result = RemovedDir(path)
                logging.debug(dir_result)
                result += dir_result
            except (NotADirectoryError, OSError):
                return result
        try:
            result += self.remove_empty_in_html_path(os.path.dirname(path))
        except ValueError:
            pass
        return result


class Converter:
    def __init__(self, template: jinja2.Template) -> None:
        super().__init__()
        self._md = md.Markdown(extensions=[
            CoreExtension(),
            'tables',
            'extra',
        ])
        self._template = template

    def convert(self, in_: TextIO, out: TextIO) -> None:
        in_str = ''
        while True:
            line = in_.readline()
            if not line:
                break
            in_str += line
        out_str = self._md.convert(in_str) + '\n'

        out.write(self._template.render(body=out_str))


class MultiConverter:
    def __init__(self, converter: Converter, file_manager: FileManager) -> None:
        self._converter = converter
        self._manager = file_manager

    def convert_all(self) -> None:
        result = self._manager.remove_all_html()
        for md_path in self._manager.get_all_md_paths():
            html_path = self._manager.get_html_path_from_md_path(md_path)
            result += self._manager.make_directory_and_ancestors(html_path)
            with open(md_path, 'r') as md_file, open(html_path, 'w+') as html_file:
                self._converter.convert(md_file, html_file)
                file_result = CreatedFile(html_path)
                logging.debug(file_result)
                result += file_result
        logging.info(result)


class IndexGenerator:
    def __init__(self, manager: FileManager, converter: Converter) -> None:
        self._manager = manager
        self._converter = converter

    def generate_indexes(self) -> None:
        result = FileChangeResult()
        for md_dir, dir_base in self._manager.get_all_md_dirs():
            if not self._manager.dir_has_md(md_dir, 'index.md'):
                result += self._generate_index(md_dir, dir_base)

    def _generate_index(self, md_dir: str, dir_base: str) -> FileChangeResult:
        html_path = self._manager.get_html_path_from_md_path(self._manager.join_md_path(md_dir, 'index.md'))
        self._manager.make_directory_and_ancestors(html_path)
        with self._get_index_md_text_io(md_dir, dir_base) as md_file, open(html_path, 'w+') as html_file:
            self._converter.convert(md_file, html_file)
            file_result = CreatedFile(html_path)
            logging.debug(file_result)
            return file_result

    def _get_index_md_text_io(self, md_dir: str, dir_base: str) -> TextIO:
        text = '# {}\n\n'.format(dir_base)
        for md_base in self._manager.get_entries_in_md_dir(md_dir):
            text += '- [{0}]({0})\n'.format(md_base)
        return StringIO(text)


class Observer(events.FileSystemEventHandler):
    def __init__(self, converter: Converter, md_root: str, html_root: str) -> None:
        super().__init__()
        self._converter = converter
        self._manager = FileManager(md_root, html_root)
        self._observer = observers.Observer()
        self._md_root = md_root

    def watch(self) -> None:
        self._observer.schedule(self, self._md_root, recursive=True)
        self._observer.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            self._observer.stop()
        self._observer.join()

    def on_moved(self, event: events.FileSystemMovedEvent) -> None:
        if event.is_directory \
                or not self._manager.is_md(event.src_path, False) \
                or not self._manager.is_md(event.dest_path):
            return

        html_old_path = self._manager.get_html_path_from_md_path(event.src_path)
        self._remove_if_exists(html_old_path)
        self._manager.remove_empty_in_html_path(html_old_path)

        html_new_path = self._manager.get_html_path_from_md_path(event.dest_path)
        self._manager.make_directory_and_ancestors(html_new_path)
        self._convert(event.dest_path, html_new_path)

    def on_created(self, event: events.FileCreatedEvent) -> None:
        if event.is_directory or not self._manager.is_md(event.src_path):
            return

        html_path = self._manager.get_html_path_from_md_path(event.src_path)
        self._manager.make_directory_and_ancestors(html_path)
        self._convert(event.src_path, html_path)

    def on_deleted(self, event: events.FileDeletedEvent) -> None:
        if event.is_directory or not self._manager.is_md(event.src_path):
            return

        html_path = self._manager.get_html_path_from_md_path(event.src_path)
        self._remove_if_exists(html_path)
        self._manager.remove_empty_in_html_path(html_path)

    def on_modified(self, event: events.FileModifiedEvent) -> None:
        if event.is_directory or not self._manager.is_md(event.src_path):
            return

        html_path = self._manager.get_html_path_from_md_path(event.src_path)
        self._convert(event.src_path, html_path)

    def _remove_if_exists(self, path: str) -> None:
        try:
            self._manager.remove_html(path)
        except ValueError:
            pass

    def _convert(self, in_path: str, out_path: str) -> None:
        out_existed = self._manager.is_html(out_path)
        with open(in_path, 'r') as in_file, open(out_path, 'w+') as out_file:
            self._converter.convert(in_file, out_file)
            result = UpdatedFile(out_path) if out_existed else CreatedFile(out_path)
            logging.info(result)

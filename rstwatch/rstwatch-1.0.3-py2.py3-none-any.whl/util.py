"""
rstwatch internal utilities
"""
import logging
import os
import re

from docutils.core import publish_file

log = logging.getLogger('rstwatch')


def list_rst_files(directory):
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1].lower() == '.rst':
            yield filename


class SourceDirectory(object):

    def __init__(self, parent, directory):
        """
        :param parent: RSTWatch instance that has configuration attributes
        :param directory: Path to the directory to be scanned
        """
        self.parent = parent
        self.directory = directory
        self.source_map = {}  # { src_basename: RSTFile instance }
        self.include_map = {}  # { include_filename: IncludeFile instance }
        self._src_include_map = {}  # { src_obj: include_filename_set }
        self._include_src_map = {}  # { include_filename: src_obj_set }

    def scan(self, refresh=False):
        """
        Scan directory for source files, update statuses, write target files.
        :param refresh:
            True if all target files should be rewritten unconditionally
        :return:
            The number of files that were written or deleted during this
            scan.
        """
        for include_obj in self.include_map.values():
            include_obj.update()
        process_list = []  # [ (src_filename, dst_filename), ... ]
        rst_files = set(self.source_map)
        rst_files.update(list_rst_files(self.directory))
        missing_rst_files = []
        for src_basename in sorted(rst_files):
            src_filename = os.path.join(self.directory, src_basename)
            if src_basename in self.source_map:
                src_obj = self.source_map[src_basename]
            else:
                src_obj = RSTFile(self, src_filename)
                self.source_map[src_basename] = src_obj
            status = src_obj.update()
            if status is None:
                missing_rst_files.append(src_basename)
            elif refresh or src_obj.target_needs_gen:
                process_list.append((src_filename, src_obj.target.filename))
        delete_list = []
        for src_basename in missing_rst_files:
            src_obj = self.source_map.pop(src_basename)
            self.unregister_include_files(src_obj)
            target = src_obj.target
            status = target.update()
            if status is None:
                # html file doesn't exist
                continue
            if status:
                # html file has been modified since last scan - don't delete
                continue
            # html file is stale - delete it
            delete_list.append((src_basename, src_obj.target.filename))
        # Execute the deletions
        for src_basename, target_filename in delete_list:
            log.info("Noticed that %r is missing, deleting %r",
                     src_basename, target_filename)
            try:
                os.remove(target_filename)
            except OSError:
                pass
        # Create/rewrite the HTML files
        for src_filename, dst_filename in process_list:
            self.convert_rst_to_html(src_filename, dst_filename)
        # Return the number of deleted or written files
        return len(delete_list) + len(process_list)

    def convert_rst_to_html(self, src_filename, dst_filename):
        log.info("Converting %s -> %s", src_filename, dst_filename)
        writer_name = self.parent.writer
        try:
            publish_file(
                source_path=src_filename,
                destination_path=dst_filename,
                writer_name=writer_name,
            )
        except Exception:
            log.exception("Error calling publish_file:"
                          " source_path=%r"
                          " destination_path=%r"
                          " writer_name=%r",
                          src_filename, dst_filename, writer_name)

    def register_include_files(self, src_obj, include_filename_set):
        """
        :param src_obj:
            An RSTFile instance
        :param include_filename_set:
            set of include file names associated with src_obj
        """
        prev_filename_set = self._src_include_map.pop(src_obj, set())
        removed_filename_set = prev_filename_set - include_filename_set
        added_filename_set = include_filename_set - prev_filename_set
        if include_filename_set:
            self._src_include_map[src_obj] = include_filename_set
        for include_filename in added_filename_set:
            if include_filename not in self.include_map:
                include_obj = IncludeFile(include_filename)
                include_obj.update()
                self.include_map[include_filename] = include_obj
            src_obj_set = self._include_src_map.setdefault(include_filename,
                                                           set())
            src_obj_set.add(src_obj)
        for include_filename in removed_filename_set:
            src_obj_set = self._include_src_map.get(include_filename, set())
            src_obj_set.discard(src_obj)
            if not src_obj_set:
                self._include_src_map.pop(include_filename, None)
                self.include_map.pop(include_filename, None)

    def unregister_include_files(self, src_obj):
        """
        :param src_obj: An RSTFile instance
        """
        self.register_include_files(src_obj, set())

    def any_include_files_newer_than_target(self, src_obj):
        """
        :param src_obj:
            An RSTFile instance
        :return:
            The list of IncludeFile instances related to src_obj that are
            newer than src_obj.target.
        """
        dst_obj = src_obj.target
        st_mtime = dst_obj.stat.st_mtime if dst_obj.stat is not None else -1.0
        include_filename_set = self._src_include_map.get(src_obj, set())
        result = []
        for include_filename in include_filename_set:
            include_obj = self.include_map.get(include_filename)
            if include_obj is None or include_obj.stat is None:
                continue
            if include_obj.stat.st_mtime > st_mtime:
                result.append(include_obj)
        return result


class ScannedFile(object):

    UNCHANGED = 0
    NEW = 1
    CHANGED = 2

    def __init__(self, filename):
        """
        :param filename: Full path to file
        """
        self.filename = filename
        self.prev_stat = None
        self.stat = None

    def update(self):
        """
        Update file status.
        :return:
            ScannedFile.NEW:
                if this is the first update and the file exists.
            ScannedFile.CHANGED:
                if the file has changed since the last update (as judged by
                st_mtime and st_size).
            ScannedFile.UNCHANGED:
                if the file has not changed since the last update.
            None:
                if the file does not exist.
        """
        self.prev_stat = self.stat
        try:
            self.stat = os.stat(self.filename)
        except OSError:
            self.stat = None
        return self.last_update_result

    @property
    def last_update_result(self):
        """
        :return:
            The result of the last call to update(), or None if update() has
            not yet been called.
        """
        if self.stat is None:
            return None
        if self.prev_stat is None:
            return self.NEW
        if (self.stat.st_mtime != self.prev_stat.st_mtime or
                self.stat.st_size != self.prev_stat.st_size):
            return self.CHANGED
        return self.UNCHANGED


class RSTFile(ScannedFile):

    def __init__(self, parent, filename):
        """
        :param parent: The containing SourceDirectory instance
        :param filename: Full path to source file
        """
        super(RSTFile, self).__init__(filename)
        self.parent = parent
        target_filename = os.path.splitext(filename)[0] + '.html'
        self.target = ScannedFile(target_filename)
        self._target_needs_gen = None

    def update(self):
        """
        Update RST file status.
        :return: The result of ScannedFile.status()
        """
        self._target_needs_gen = None
        status = super(RSTFile, self).update()
        if status is None:
            # File no longer exists
            self.parent.unregister_include_files(self)
            return None
        if status:
            # File is new or changed since last update
            self._scan_for_include_files()
        return status

    @property
    def target_needs_gen(self):
        """
        Call the update() method before accessing this property.
        :return: True iff the target file should be (re)generated.
        """
        if self._target_needs_gen is None:
            self._target_needs_gen = self._calc_target_needs_gen()
        return self._target_needs_gen

    def _calc_target_needs_gen(self):
        if self.stat is None:
            # Source file does not exist
            return False
        target_status = self.target.update()
        if target_status is None:
            # Target file doesn't exist, must generate it
            return True
        if self.parent.any_include_files_newer_than_target(self):
            return True
        if self.last_update_result == self.CHANGED:
            return True
        return self.stat.st_mtime > self.target.stat.st_mtime

    def _scan_for_include_files(self):
        include_filename_set = set()
        filename = self.filename
        try:
            with open(filename, 'r') as f:
                for line in f:
                    m = re.match(r'^..\s+include::\s+(\S+)', line)
                    if not m:
                        continue
                    include_filename = m.group(1)
                    full_include_filename = os.path.normpath(
                        os.path.join(self.parent.directory, include_filename))
                    include_filename_set.add(full_include_filename)
        except Exception:
            log.exception("Error scanning %r for include files.",
                          filename)
        self.parent.register_include_files(self, include_filename_set)


class IncludeFile(ScannedFile):
    pass

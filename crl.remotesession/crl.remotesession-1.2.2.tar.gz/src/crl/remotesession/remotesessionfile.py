import shutil
import os
import tempfile
from .remotesessiontarget import RemoteSessionTarget


__copyright__ = 'Copyright (C) 2019, Nokia'


class RemoteSessionFile(RemoteSessionTarget):

    def copy_file_between_targets(self,
                                  from_target,
                                  source_file,
                                  to_target,
                                  destination_dir='.',
                                  mode='0755',
                                  timeout=3600):
        """
        Copy file from one remote target to another.

        **Arguments:**

        *from_target*: Source target.

        *source_file*: Source file.

        *to_target*: Destination target.

        *destination*: Destination directory or file.

        *mode*: Access mode to set to the file in the destination target.

        *timeout*: Timeout in seconds.

        **Returns:**

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        **Example:**

        +---------+---------+--------------+---------+---------------+
        | Copy    | default | /tmp/foo.tgz | target2 | /tmp/backups/ |
        | File    |         |              |         |               |
        | Between |         |              |         |               |
        | Targets |         |              |         |               |
        +---------+---------+--------------+---------+---------------+
        """
        efrom = self._get_engine(from_target)
        eto = self._get_engine(to_target)
        copyf = (efrom.copy_file_between_targets
                 if efrom == eto else
                 self._copy_file_between_targets)
        return self._getresult(copyf(from_target,
                                     source_file,
                                     to_target,
                                     destination_dir=destination_dir,
                                     mode=mode,
                                     timeout=timeout))

    def _copy_file_between_targets(self,
                                   from_target,
                                   source_file,
                                   to_target,
                                   destination_dir='.',
                                   mode='0755',
                                   timeout=3600):
        tmpd = tempfile.mkdtemp()
        try:
            self.copy_file_from_target(source_file,
                                       destination=tmpd,
                                       target=from_target,
                                       timeout=timeout)
            return self.copy_file_to_target(
                os.path.join(tmpd, source_file),
                destination_dir=destination_dir,
                mode=mode,
                target=to_target,
                timeout=timeout)
        finally:
            shutil.rmtree(tmpd)

    def copy_file_from_target(self,
                              source_file,
                              destination=None,
                              target='default',
                              timeout=3600):
        """
        Copy file from the target to local host.

        **Arguments:**

        *source_file*: Target source file.

        *destination*: Local destination directory or file.

        *target*: Target where to copy the file from.

        *timeout*: Timeout in seconds.

        **Returns:**

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        **Example:**

        +----------------------------+-------------------------------+
        | Execute Command In Target  | mkdir /tmp/my-robot-tc &&     |
        |                            | touch /tmp/my-robot-tc/bar.sh |
        +----------------------------+-------------------------------+
        | Copy File From Target      | /tmp/my-robot-tc/bar.sh       |
        +----------------------------+-------------------------------+

        """
        return self._getresult(
            self._get_engine(target).copy_file_from_target(
                source_file,
                destination=destination,
                target=target,
                timeout=timeout))

    def copy_file_to_target(self,
                            source_file,
                            destination_dir='.',
                            mode='0755',
                            target='default',
                            timeout=3600):
        """
        Copy file from local host to the target.

        **Arguments:**

        *source_file:*  Local source file.

        *destination*: Remote destination directory or file (files
        and directories are distinguished by *os.path.basename* which
        is an empty string in case of dirctory.) If directories do not
        exist, they are created.

        *mode*: Access mode to set to the file in the target.

        *target*: Target where to copy the file.

        *timeout*: Timeout in seconds.

        **Returns:**

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        **Example:**

        +---------------------+--------+-----------------------+
        | Copy File To Target | foo.sh | /tmp/my-robot-tc/     |
        +---------------------+--------+-----------------------+

        """
        return self._getresult(
            self._get_engine(target).copy_file_to_target(
                source_file,
                destination_dir=destination_dir,
                mode=mode,
                target=target,
                timeout=timeout))

    def copy_directory_to_target(self,
                                 source_dir,
                                 target_dir='.',
                                 mode='0755',
                                 target='default',
                                 timeout=3600):
        """
        Copies contents of local source directory to remote destination
        directory.

        **Arguments:**

        *source_dir*: Local source directory whose contents are copied to the
        target.

        *target_dir*: Remote destination directory that will be created if
        missing.

        *mode*: Access mode to set to the files and directories copied
        to the target.

        *target*: Target where to copy the file.

        *timeout*: Timeout in seconds.

        **Returns:**

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        **Example:**

        +----------------+---------+---------------------------+
        | Copy Directory | scripts | /tmp/my-robot-tc/scripts/ |
        | To Target      |         |                           |
        +----------------+---------+---------------------------+

        """
        return self._getresult(
            self._get_engine(target).copy_directory_to_target(
                source_dir,
                target_dir=target_dir,
                mode=mode,
                target=target,
                timeout=timeout))

    def create_directory_in_target(self,
                                   path,
                                   mode='0755',
                                   target='default',
                                   timeout=3600):
        """
        Create a directory including missing parent directories in the target.

        **Arguments:**

        *path*: Remote directory to create.

        *mode*: Access mode to set to the directory in the target.

        *target*: Target where to create the file.

        *timeout* Timeout in seconds.

        **Returns:**

        Python *namedtuple* with arguments *status*, *stdout* and *stderr*.

        """
        return self._getresult(
            self._get_engine(target).create_directory_in_target(
                path,
                mode=mode,
                target=target,
                timeout=timeout))

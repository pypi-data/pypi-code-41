import os, itertools, shutil
from multiprocessing import Value, Pool, Lock, current_process
from sil import Sil
from .utils import (
    filelines, linesplit, linemend,
    superdirs, readlines_split, dir_from_cols,
    sharddir, shardname, shardloc
)

default_sil_options = {
    'length': 40,
    'every': 1
}

class ParPar:
    def __init__(self):
        pass

    def shard(self,
        input_file: str,
        output_dir: str,
        columns: list,
        delim: str = '\t',
        newline: str = '\n',
        sil_opts:dict = default_sil_options
    )->list:
        '''
        Given the `input_file` and the column indicies, reads each line of the
        `input_file` and dumps the content into a file in the directory:

            output_dir/<columns[0]>/.../<columns[N]>/basename(<input_file>)

        where <columns[i]> is the value found in the current line at position i
        after being split by the specified `delim`.

        WARNINGS:
            everything in specified `output_dir` will be PERMANENTLY REMOVED.

        Arguments:
            input_file (str): full path to the file to be sharded.

            output_dir (str): full path to a directory in which to dump. WARNING:
                everything in specified directory will be PERMANENTLY REMOVED.

            columns (list): the columns (indices) across which to shard. The
                values found in these columns will be used as directory
                names (nested).

            delim (str): How to split each field in a line of the file.
                Defaults to '\t'.

            newline (str): How to split each line of the file. Defaults to '\n'.

            sil_opts (dict): Defaults to {'length': 40, 'every': 1}. See the
                Sil package.

        Returns:
            sharded_files (list): list of all the sharded files
        '''
        lno = filelines(input_file) # number of lines in the input_file
        sts = Sil(lno, **sil_opts)  # status indicator
        basename = os.path.basename(input_file)
        files_made = set({})
        file_objs = {}

        # delete current `output_dir` if it already exists
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)

        with open(input_file, 'r') as f:
            for line in f:
                fields = linesplit(line, delim, newline)
                dest = dir_from_cols(fields, columns)
                files_made.add(dest)
                dir_path = os.path.join(output_dir, dest)
                if not os.path.isdir(dir_path):
                    os.makedirs(dir_path)
                    file_objs[dir_path] = open(os.path.join(dir_path, basename), 'a')

                o = file_objs[dir_path]
                o.write(linemend(fields, delim, newline))
                suffix = '\t{} files made'.format(len(files_made))
                sts.tick(suffix=suffix)

        # close all made file objects
        for fo in file_objs.values():
            fo.close()

        return self.shard_files(output_dir)

    def shard_by_lines(self,
        input_file:str,
        output_dir:str,
        number_of_lines:int,
        sil_opts:dict = default_sil_options
    )->list:
        '''
        Given the input_file and the columns, reads each line of the input_file
        into output files in subdirectories labeled by the line numbers
        `'start_stop'` based on the value `number_of_lines`:

            output_dir/<n>_<n+number_of_lines>/basename(<input_file>)

        WARNINGS:
            everything in specified `output_dir` will be PERMANENTLY REMOVED.

        Arguments:
            input_file (str): full path to the file to be sharded.

            output_dir (str): full path to a directory in which to dump. WARNING:
                everything in specified directory will be PERMANENTLY REMOVED.

            number_of_lines (int): the number of lines which should be at most in
                each sharded file.

            sil_opts (dict): Defaults to `{'length': 40, 'every': 1}`. See the
                Sil package.

        Returns:
            sharded_files (list): list of all the sharded files
        '''
        lno = filelines(input_file)
        sts = Sil(lno, **sil_opts)
        basename = os.path.basename(input_file)

        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)

        with open(input_file, 'r') as f:
            tally = 0
            while tally < lno:
                if tally % number_of_lines == 0:

                    dest = '{}_{}'.format(tally, tally+number_of_lines)

                    dir_path = os.path.join(output_dir, dest)
                    if not os.path.isdir(dir_path):
                        os.makedirs(dir_path)
                    with open(os.path.join(dir_path, basename), 'a') as o:
                        for i in range(number_of_lines):
                            line = f.readline()
                            if not line:
                                break
                            o.write(line)
                            sts.tick()
                        tally += number_of_lines


        return self.shard_files(output_dir)

    def shard_files(self, directory:str)->list:
        '''
        Arguments:
            directory (str): The top-most directory of a shared file.

        Returns:
            (list): The list of all files under directory (regardless of depth).
        '''
        file_paths = []
        for path, subdirs, files in os.walk(directory):
            if not files: continue
            file_paths += [
                os.path.join(path, f) for f in files
                if 'DS_Store' not in f
            ]
        return file_paths

    def shard_walk(self, directory:str)->dict:
        '''
        Arguments:
            directory (str): The top-most directory of a shared file.

        Returns:
            (dict): A nested dictionary containing the folder names found at
                each level. The bottom-most level of the dictionary contains files
                found.

                e.g.  if in directory there was directory/key_1/key_2/file_1
                {
                    key_1: {
                        key: 2: [ file_1, ...]
                    }

                }
        '''
        walk = {}
        for path, subdirs, files in os.walk(directory):
            supdirs = superdirs(path, directory)
            drilldown = walk

            for i, key in enumerate(supdirs):
                if key not in drilldown:
                    leaf_q = (files and i == len(supdirs) - 1)
                    drilldown[key] = [] if leaf_q else {}

                drilldown = drilldown[key]

            if files:
                drilldown += files

        return walk

    def shard_keys(self, directory:str)->list:
        '''
        Arguments:
            directory (str): The top-most directory of a shared file.

        Returns:
            (list): A list of lists for the directory names found at each level
                after under directory
                e.g.

                directory
                    key_1
                        key_a
                        key_b
                    key_2
                        ...
                returns
                [ [key_1, key_2, ...], [key_a, key_b, ...], ... ]
        '''
        level_keys = []
        for path, subdirs, files in os.walk(directory):
            supdirs = superdirs(path, directory)
            if len(level_keys) > len(supdirs):
                level_keys[len(supdirs)] += subdirs
            else:
                level_keys.append(subdirs)
        return [list(set(keys)) for keys in level_keys]

    def sharded_records(self, files:str=None, directory:str=None)->int:
        '''
        Notes:
            Assumes each line in each subfile is a record.
        Arguments:
            files (str): The files from which to tabulate records. By default
                `None`, resulting in `shard_files(directory)` being called.
            directory (str): The top-most directory of a shared file.

        Returns:
            (int): Total number of lines in all leaf files under directory.
        '''
        if files is None and directory is not None: files = self.shard_files(directory)

        return sum([filelines(f) for f in files])


    def assemble_shard(self, directory:str, delim:str='\t', newline:str='\n')->list:
        '''
        Arguments:
            directory (str): The top-most directory of a shared file.

        Keyword Arguments:
            delim (str): Defaults to '\t'
            newline (str): Defaults to '\n'

        Returns:
            (list): The list of lists, where each sub-list is a record found
                in one of the sharded leaf files after being split by delim.
                (i.e. all records are returned together)
        '''
        results = []
        files = self.shard_files(directory)


        with Pool(processes=os.cpu_count()) as pool:
            sarg = [(f, delim, newline) for f in files]
            lines = pool.starmap(readlines_split, sarg)

        return list(itertools.chain.from_iterable(lines))



    _shared_current = Value('i', 0)
    _shared_lock = Lock()

    def shard_line_apply(self,
        directory:str,
        function,
        args:list=[],
        kwargs:dict={},
        processes:int=None,
        sil_opts:dict=default_sil_options
    ):
        '''
        Parallelizes `function` across each _line_ of the sharded files found as
        the leaves of `directory`.

        Notes:
            - if `processes` is None, **all** of them will be used i.e.
                `os.cpu_count()`

            - Several keywords for `kwargs` are reserved:
                1. lock:          a lock, if needed, to prevent race conditions.
                2. full_path:     the full path to the file which was opened.
                3. relative_path: the path under (directory) to the file which
                                  was opened.
                4. output_shard_name: if provided will rename the shard
                5. output_shard_loc:  if provided will move the shard

        Arguments:
            directory (str): The top-most directory of a shared file.

            function (func): The function which will be parallelized. This
                function **MUST** be defined so that it can be called as:
                    `function(line, *args, **kwargs)`

        Keyword Arguments:
            args (list): arguments to be passed to `function` on each thread.

            kwargs (dict): key-word arguments to be passed to `function` on each
                thread.

            processes (int): The number of processes to spawn. Defaults to
                **ALL** availble cpu cores on the calling computer.

            sil_opts (dict): Defaults to `{'length': 40, 'every': 1}`.
                See the Sil package.
        Returns:
            None
        '''
        if processes is None: processes = os.cpu_count()
        sfiles = self.shard_files(directory)
        records = self.sharded_records(sfiles)
        sts = Sil(records, **sil_opts)

        with Pool(processes=processes) as pool:
            self._shared_current.value = -1

            sargs = [
                (directory, file, sts, function, args, kwargs) for file in sfiles
            ]
            results = pool.starmap(self._shard_line_apply, sargs)

            pool.close()
            pool.join()
            pool.terminate()
        return results


    def _shard_line_apply(self,
        directory:str,
        file:str,
        status,
        function,
        args:list,
        kwargs:dict
    ):
        # multiprocessing.Lock
        kwargs['lock']            = self._shared_lock
        # multiprocessing.Value (shared memory counter for progress bar)
        kwargs['shared_current']  = self._shared_current
        # an instance of Sil
        kwargs['status']          = status

        # full path to the current sharded file being processes
        kwargs['full_path']       = file
        kwargs['shard_name']      = shardname(file, directory)
        kwargs['shard_dir']       = sharddir(file, directory)
        kwargs['shard_loc']       = shardloc(file, directory)
        kwargs['relative_path']   = os.path.join(*superdirs(file, directory))
        kwargs['current_process'] = current_process().name


        cp = kwargs['current_process']

        force_overwrite = kwargs['force_overwrite'] if 'force_overwrite' in kwargs else True

        os_name = kwargs['output_shard_name'] if 'output_shard_name' in kwargs else None
        os_loc  = kwargs['output_shard_loc']  if 'output_shard_loc'  in kwargs else kwargs['shard_loc']

        if os_name is not None:
            dest = os.path.join(os_loc, os_name, os.path.dirname(kwargs['relative_path']))
            kwargs['dest'] = dest
            self._shared_lock.acquire()
            try:
                if os.path.isdir(dest):
                    if force_overwrite:
                        shutil.rmtree(dest)
                else:
                    os.makedirs(dest)
            finally:
                self._shared_lock.release()


        with open(file, 'r') as f:
            for line in f:
                function(line, *args, **kwargs)
                self._shared_lock.acquire()
                try:
                    self._shared_current.value += 1
                    suffix = '\tprocess: {}'.format(cp)
                    status.update(current=self._shared_current.value, suffix=suffix)
                finally:
                    self._shared_lock.release()


    def shard_file_apply(self,
        directory:str,
        function,
        args:list=[],
        kwargs:dict={},
        processes:int=None,
        sil_opts:dict=default_sil_options,
        shard_files:list=None
    ):
        '''
        Parallelizes `function` across each of the sharded files found as
        the leaves of `directory`.

        Notes:
            - if `processes` is None, **all** of them will be used i.e.
                `os.cpu_count()`

            - Several keywords for `kwargs` are reserved:
                1. lock:          a lock, if needed, to prevent race conditions.
                2. full_path:     the full path to the file which was opened.
                3. relative_path: the path under (directory) to the file which
                                  was opened.
                4. output_shard_name: if provided will rename the shard
                5. output_shard_loc:  if provided will move the shard

        Arguments:
            directory (str): The top-most directory of a shared file.

            function (func): The function which will be parallelized. This
                function **MUST** be defined so that it can be called as:
                    `function(line, *args, **kwargs)`

        Keyword Arguments:
            args (list): arguments to be passed to `function` on each thread.

            kwargs (dict): key-word arguments to be passed to `function` on each
                thread.

            processes (int): The number of processes to spawn. Defaults to
                **ALL** availble cpu cores on the calling computer.

            sil_opts (dict): Defaults to `{'length': 40, 'every': 1}`.
                See the Sil package.
        Returns:
            None
        '''
        if processes is None: processes = os.cpu_count()
        if shard_files is None:
            sfiles = self.shard_files(directory)
        else:
            sfiles = shard_files
        try:
            records = self.sharded_records(sfiles)
        except Exception:
            records = len(sfiles)
        sts = Sil(records, **sil_opts)

        maxtasksperchild = None if 'maxtasksperchild' not in kwargs else kwargs['maxtasksperchild']

        with Pool(processes=processes, maxtasksperchild=maxtasksperchild) as pool:
            self._shared_current.value = -1

            sargs = [
                (directory, file, sts, function, args, kwargs) for file in sfiles
            ]
            pool.starmap(self._shard_file_apply, sargs)

            pool.close()
            pool.join()
            pool.terminate()


    def _shard_file_apply(self,
        directory:str,
        file:str,
        status,
        function,
        args:list,
        kwargs:dict
    ):
        # multiprocessing.Lock
        kwargs['lock']            = self._shared_lock
        # multiprocessing.Value (shared memory counter for progress bar)
        kwargs['shared_current']  = self._shared_current
        kwargs['status']          = status
        kwargs['full_path']       = file
        kwargs['shard_name']      = shardname(file, directory)
        kwargs['shard_dir']       = sharddir(file, directory)
        kwargs['shard_loc']       = shardloc(file, directory)
        kwargs['relative_path']   = os.path.join(*superdirs(file, directory))
        kwargs['current_process'] = current_process().name

        force_overwrite = kwargs['force_overwrite'] if 'force_overwrite' in kwargs else True


        os_name = kwargs['output_shard_name'] if 'output_shard_name' in kwargs else None
        os_loc = kwargs['output_shard_loc'] if 'output_shard_loc' in kwargs else kwargs['shard_loc']

        if os_name is not None:
            dest = os.path.join(os_loc, os_name, os.path.dirname(kwargs['relative_path']))
            kwargs['dest'] = dest
            self._shared_lock.acquire()
            try:
                if os.path.isdir(dest):
                    if force_overwrite:
                        shutil.rmtree(dest)
                else:
                    os.makedirs(dest)
            finally:
                self._shared_lock.release()


        function(file, *args, **kwargs)

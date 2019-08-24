import os


class FileWriter:
    def __init__(self, filename, directory=None, mode='w', batch_size=1, extract_filename=None, total_buffer_size=10000):
        self.filename = filename
        self.directory = directory
        self.batch_size = batch_size
        self.mode = mode
        self.extract_filename = extract_filename
        self.total_buffer_size = total_buffer_size

        self._total_buffer_size = 0
        self._fds = {}
        self._buffer = {}

    def fd(self, filename=None):
        if not filename:
            filename = 'default'

        if filename not in self._fds:
            self._fds[filename] = self.generate_fd(filename)

        return self._fds[filename]

    def generate_fd(self, filename=None):
        if not filename:
            filename = self.filename

        formatted_filename = self.format_filename(filename)

        dirname = os.path.dirname(formatted_filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        return open(formatted_filename, self.mode)

    def write_line(self, line):
        if self.extract_filename:
            filename = self.extract_filename(line)
        else:
            filename = self.filename

        fd = self.fd(filename)
        fd.write(line)
        fd.write('\n')

    def format_filename(self, filename: str):
        if self.directory and not filename.startswith(self.directory):
            formatted_filename = os.path.join(self.directory, filename)
        else:
            formatted_filename = filename

        return formatted_filename

    def close_fds(self):
        for k in self._fds:
            fd = self._fds.pop(k)
            fd.close()

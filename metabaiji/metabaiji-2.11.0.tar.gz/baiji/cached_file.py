import os
from baiji import path
from baiji.exceptions import KeyNotFound, KeyExists

class FileMode(object):
    def __init__(self, mode, allowed_modes=None):
        self.mode = mode
        self._modes = set(mode)
        if self._modes - set('arwxb+tU') or len(self.mode) > len(self._modes):
            raise ValueError('Invalid mode')
        if allowed_modes:
            if self._modes - set(allowed_modes):
                raise NotImplementedError('CachedFile does not support mode %s' % "".join(self._modes - set(allowed_modes)))

        if 'U' in self._modes:
            raise NotImplementedError('s3.open does not support universal newline mode')
        self.reading = 'r' in self._modes
        self.writing = 'w' in self._modes
        self.creating_exclusively = 'x' in self._modes
        self.appending = 'a' in self._modes
        self.updating = '+' in self._modes
        self.text = 't' in self._modes
        self.binary = 'b' in self._modes
        if self.text and self.binary:
            raise ValueError("can't have text and binary mode at once")
        if self.reading + self.writing + self.appending + self.creating_exclusively > 1:
            raise ValueError("can't have read/write/append/exclusive create mode at once")
        if not (self.reading or self.writing or self.appending or self.creating_exclusively):
            raise ValueError("must have exactly one of read/write/append/exclusive create mode")

    @property
    def is_output(self):
        return self.writing or self.appending or self.creating_exclusively

    @property
    def flags(self):
        '''
        Adapted from http://hg.python.org/cpython/file/84cf25da86e8/Lib/_pyio.py#l154

        See also open(2) which explains the modes

        os.O_BINARY and os.O_TEXT are only available on Windows.
        '''
        return (
            ((self.reading and not self.updating) and os.O_RDONLY or 0) |
            ((self.writing and not self.updating) and os.O_WRONLY or 0) |
            ((self.creating_exclusively and not self.updating) and os.O_EXCL or 0) |
            (self.updating and os.O_RDWR or 0) |
            (self.appending and os.O_APPEND or 0) |
            ((self.writing or self.creating_exclusively) and os.O_CREAT or 0) |
            (self.writing and os.O_TRUNC or 0) |
            ((self.binary and hasattr(os, 'O_BINARY')) and os.O_BINARY or 0) |
            ((self.text and hasattr(os, 'O_TEXT')) and os.O_TEXT or 0)
        )

class CachedFile(object):
    '''
    CachedFile('s3://bucket/path/to/file.ext', 'r') downloads the file and opens it for reading
    CachedFile('s3://bucket/path/to/file.ext', 'w') opens a temp file for writing and uploads it on close
    CachedFile('s3://bucket/path/to/file.ext', 'x') verifies that the file doesn't exist on s3, then behaves like 'w'
    '''
    def __init__(self, key, mode='r', connection=None, encrypt=True, version_id=None):
        from baiji.connection import S3Connection
        self.encrypt = encrypt
        self.key = key
        if path.islocal(key):
            self.should_upload_on_close = False
            self.mode = FileMode(mode, allowed_modes='arwxb+t')
            import __builtin__
            local_path = path.parse(key).path
            if self.mode.is_output and not os.path.exists(os.path.dirname(local_path)):
                from baiji.util.shutillib import mkdir_p
                mkdir_p(os.path.dirname(local_path))
            try:
                # Use os.open to catch exclusive access to the file, but use open to get a nice, useful file object
                self.fd = os.open(local_path, self.mode.flags)
                self.f = __builtin__.open(local_path, self.mode.mode.replace('x', 'w'))
                os.close(self.fd)
            except OSError as e:
                import errno
                if e.errno is errno.EEXIST:
                    raise KeyExists("Local file exists: %s" % local_path)
                elif e.errno is errno.ENOENT:
                    raise KeyNotFound("Local file does not exist: %s" % local_path)
                else:
                    raise IOError(e.errno, "%s: %s" % (e.strerror, e.filename))
        else:
            if connection is None:
                connection = S3Connection()
            self.connection = connection

            self.mode = FileMode(mode, allowed_modes='rwxbt')
            self.should_upload_on_close = self.mode.is_output
            if self.mode.creating_exclusively:
                if self.connection.exists(self.key):
                    raise KeyExists("Key exists in bucket: %s" % self.key)
                else:
                    self.connection.touch(self.key, encrypt=self.encrypt)
            # Use w+ so we can read back the contents in upload()
            new_mode = (
                'w+' +
                (self.mode.binary and 'b' or '') +
                (self.mode.text and 't' or '')
            )
            from baiji.util import tempfile
            self.f = tempfile.NamedTemporaryFile(
                mode=new_mode,
                suffix=os.path.splitext(path.parse(self.key).path)[1]
            )
            self.name = self.f.name
            self.remotename = key # Used by some serialization code to find files which sit along side the file in question, like textures which sit next to a mesh file
            if self.mode.reading:
                self.connection.cp(self.key, self.name, force=True, version_id=version_id)
    def upload(self):
        self.connection.cp(self.name, self.key, encrypt=self.encrypt, force=True)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        # If an unhandled exception is bubbling up, don't write to s3!
        if exc_value:
            self.should_upload_on_close = False
        self.close()
    def __getattr__(self, attr):
        return getattr(self.f, attr)
    def __iter__(self):
        return iter(self.f)
    def flush(self):
        self.f.flush()
        if self.should_upload_on_close:
            self.upload()
    def close(self):
        self.flush()
        self.f.close()

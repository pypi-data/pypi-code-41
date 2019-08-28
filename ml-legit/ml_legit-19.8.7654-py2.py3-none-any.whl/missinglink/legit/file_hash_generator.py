import hashlib


SHA_CACHE_KEY = 'ai.ml.sha'


class FileHashGenerator(object):

    has_xattr_support = False

    @classmethod
    def hash_file(cls, file_name, st_mtime=None, st_size=None, should_hash_file_stats=False):
        """

        Args:
            file_name (str):
            st_mtime (float): size of file, in bytes
            st_size (int): platform dependent; time of most recent metadata change on Unix,
            should_hash_file_stats (bool): default to hash the file by it's content

        Returns:
            str - file SHA1 hash
        """

        attr_mtime, attr_sha = cls._get_xattr(file_name)

        if attr_mtime == str(st_mtime):
            return attr_sha

        if should_hash_file_stats:
            sha = cls._file_stats_to_hash(file_name, st_mtime, st_size)
        else:
            sha = cls._file_content_to_hash(file_name)

        cls._set_xattr(file_name, st_mtime, sha)

        return sha

    @classmethod
    def _file_content_to_hash(cls, file_name):
        sha_1 = hashlib.sha1()

        buffer_size = 1024 * 1024  # 1MB
        with open(file_name, 'rb') as f:
            for chunk in iter(lambda: f.read(buffer_size), b''):
                sha_1.update(chunk)

        return sha_1.hexdigest()

    @classmethod
    def _file_stats_to_hash(cls, file_name, st_mtime, st_size):
        sha_1 = hashlib.sha1()

        data_string = '{file_name}|{st_mtime}|{st_size}'.format(
            file_name=file_name,
            st_mtime=st_mtime,
            st_size=st_size,
        )

        data_encoded = data_string.encode()
        sha_1.update(data_encoded)

        return sha_1.hexdigest()

    @classmethod
    def file_etag_to_hash(cls, etag):
        sha_1 = hashlib.sha1()

        etag_encoded = etag.encode('ascii')
        sha_1.update(etag_encoded)

        return sha_1.hexdigest()

    @classmethod
    def _get_xattr(cls, path):
        attr = ExtendedFileAttributes(path) if cls.has_xattr_support else None

        if not attr:
            return None, None

        try:
            data = attr.get(SHA_CACHE_KEY)
            data = data.decode()
            data = data.split('|')
            data[0] = data[0]
        except (IOError, OSError):
            data = (None, None)

        return data

    @classmethod
    def _set_xattr(cls, path, mtime, sha):

        if not cls.has_xattr_support:
            return

        data_encoded = '%s|%s' % (mtime, sha)
        data_encoded = data_encoded.encode()
        try:
            ExtendedFileAttributes(path).set(SHA_CACHE_KEY, data_encoded)
        except (IOError,) as ex:
            if ex.errno == 95:
                cls.has_xattr_support = False
                return

            if ex.errno == 13:  # Permission denied
                return

            raise


try:
    from xattr import xattr as ExtendedFileAttributes
    FileHashGenerator.has_xattr_support = True
except ImportError:
    FileHashGenerator.has_xattr_support = False

    class ExtendedFileAttributes(object):

        def __init__(self, path):
            pass

        def set(self, key, value):
            return None

        def get(self, key):
            return None

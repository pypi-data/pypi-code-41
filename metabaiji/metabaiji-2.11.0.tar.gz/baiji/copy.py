import os
from baiji.util.parallel import ParallelWorker
from baiji.exceptions import InvalidSchemeException, S3Exception, KeyNotFound, KeyExists, get_transient_error_class

S3_MAX_UPLOAD_SIZE = 1024*1024*1024*5 # 5gb

class S3CopyOperation(object):
    class CopyableKey(object):
        def __init__(self, key, connection):
            import re
            from baiji import path
            self.raw = key
            self.connection = connection
            self.parsed = path.parse(key)
            self.remote_path = None # value here will be set by the path setting, this just satisfies lint
            self.isdir = path.isdirlike(key)
            self.path = self.parsed.path
            if not (self.path.startswith(path.sep) or re.match(r'^[a-zA-Z]:', self.path)):
                self.path = path.sep + self.path
            self.bucket_name = self.parsed.netloc
            self.scheme = self.parsed.scheme
            if self.scheme not in ['file', 's3']:
                raise InvalidSchemeException("URI Scheme %s is not implemented" % self.scheme)
        @property
        def path(self):
            return self._path
        @path.setter
        def path(self, val):
            from baiji.util.munging import _strip_initial_slashes
            self._path = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init
            # For remote operations, we need a path without initial slashes
            self.remote_path = _strip_initial_slashes(self.path)
        @property
        def bucket(self):
            return self.connection._bucket(self.bucket_name) # pylint: disable=protected-access
        @property
        def uri(self):
            if self.is_file:
                return self.path
            else:
                return "s3://" + self.bucket_name + self.path
        @property
        def is_file(self):
            return self.scheme == 'file'
        @property
        def is_s3(self):
            return self.scheme == 's3'
        def exists(self):
            return self.connection.exists(self.uri)
        def etag(self):
            return self.connection.etag(self.uri)
        def rm(self):
            return self.connection.rm(self.uri)
        def lookup(self, version_id=None):
            from baiji.util.lookup import get_versioned_key_remote

            if self.is_file:
                raise ValueError("S3CopyOperation.CopyableKey.lookup called for local file")

            key = get_versioned_key_remote(self.bucket, self.remote_path, version_id=version_id)

            if not key:
                raise KeyNotFound("Error finding %s on s3: doesn't exist" % (self.uri))
            return key

        def create(self):
            if self.is_file:
                raise ValueError("S3CopyOperation.CopyableKey.create called for local file")
            from boto.s3.key import Key
            key = Key(self.bucket)
            key.key = self.remote_path

            return key

    def __init__(self, src, dst, connection):
        '''
        Both src and dst may be files or s3 keys
        '''
        from os import path
        self.connection = connection
        self.src = self.CopyableKey(src, connection)
        self.dst = self.CopyableKey(dst, connection)
        self.task = (self.src.scheme, self.dst.scheme)

        if self.src.isdir:
            raise ValueError("{} is a directory (not copied; use recursive mode to copy directories".format(self.src.raw))

        if self.dst.isdir:
            self.dst.path = path.join(self.dst.path, path.basename(self.src.path))

        # DEFAULTS:
        self.progress = False
        self.force = False
        self.policy = None
        self.preserve_acl = False
        self.encrypt = False
        self.encoding = None
        self.gzip = False
        self.content_type = None
        self.metadata = {}
        self.skip = False
        self.max_size = S3_MAX_UPLOAD_SIZE

        self.retries_allowed = 1
        self._retries = 0

        self.file_size = None
        # s3 version
        self._version_id = None

    @property # read only
    def retries_made(self):
        return self._retries

    @property
    def policy(self):
        return self._policy
    @policy.setter
    def policy(self, val):
        if val and self.dst.is_file:
            raise ValueError("Policy only allowed when copying to s3")
        self._policy = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def version_id(self):
        return self._version_id
    @version_id.setter
    def version_id(self, val):
        self._version_id = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init


    @property
    def preserve_acl(self):
        return self._preserve_acl
    @preserve_acl.setter
    def preserve_acl(self, val):
        val = bool(val)
        if val and self.task != ('s3', 's3'):
            raise ValueError("Preserve ACL only allowed when copying from s3 to s3")
        self._preserve_acl = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def progress(self):
        return self._progress
    @progress.setter
    def progress(self, val):
        val = bool(val)
        self._progress = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def force(self):
        return self._force
    @force.setter
    def force(self, val):
        val = bool(val)
        self._force = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def skip(self):
        return self._skip_exist
    @skip.setter
    def skip(self, val):
        val = bool(val)
        self._skip_exist = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def encrypt(self):
        return self._encrypt
    @encrypt.setter
    def encrypt(self, val):
        val = bool(val) and self.dst.is_s3
        self._encrypt = val  # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def validate(self):
        return self._validate
    @validate.setter
    def validate(self, val):
        self._validate = bool(val) # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def encoding(self):
        return self._encoding
    @encoding.setter
    def encoding(self, val):
        if val is not None and self.dst.is_file:
            raise ValueError("Encoding can only be specified when copying to s3")
        if val is not None and self.gzip and val != 'gzip':
            raise ValueError("gzip overrides explicit encoding")
        self._encoding = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def gzip(self):
        return self._gzip
    @gzip.setter
    def gzip(self, val):
        val = bool(val)
        if val and self.task != ('file', 's3'):
            raise ValueError("gzip can only be specified when uploading to s3")
        if val and self.encoding is not None and self.encoding != 'gzip':
            raise ValueError("gzip overrides explicit encoding")
        self._gzip = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def max_size(self):
        return self._max_size
    @max_size.setter
    def max_size(self, val):
        if val is None:
            val = S3_MAX_UPLOAD_SIZE
        self._max_size = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    @property
    def content_type(self):
        return self._content_type
    @content_type.setter
    def content_type(self, val):
        if val is not None and self.dst.is_file:
            raise ValueError("Content Type can only be specified when copying to s3")
        self._content_type = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init
    def guess_content_type(self):
        import mimetypes
        content_type, _ = mimetypes.guess_type(self.src.path)
        if not content_type and self.is_extensionless_html():
            content_type = 'text/html'
        elif not content_type:
            content_type = 'application/octet-stream'
        self.content_type = content_type
    def is_extensionless_html(self):
        # test if file has no extension and html5 doctype in first 100 bytes
        if os.path.splitext(self.src.path)[-1] == '':
            if self.encoding == 'gzip':
                import gzip
                with gzip.open(self.src.path, 'rb') as f:
                    return '<!DOCTYPE html>' in f.read(100)
            else:
                with open(self.src.path, 'r') as f:
                    return '<!DOCTYPE html>' in f.read(100)
        else:
            return False


    @property
    def metadata(self):
        meta = self._metadata
        if self.encoding is not None:
            meta['Content-Encoding'] = self.encoding
        if self.content_type is not None:
            meta['Content-Type'] = self.content_type
        return meta
    @metadata.setter
    def metadata(self, val):
        if not (val is None or val == {}) and self.dst.is_file:
            raise ValueError("Metadata can only be specified when copying to s3")
        if val is None:
            val = {}
        self._metadata = val # we get initialized with a call to the setter in init pylint: disable=attribute-defined-outside-init

    def execute(self):
        from boto.s3.connection import S3ResponseError
        if not self.force and self.dst.exists():
            if self.skip:
                import warnings
                warnings.warn("Skipping existing destination copying %s to %s: Destinaton exists" % (self.src.uri, self.dst.uri))
                return
            else:
                raise KeyExists("Error copying %s to %s: Destinaton exists" % (self.src.uri, self.dst.uri))

        if self.dst.is_file:
            self.prep_local_destination()

        try:
            if self.task == ('file', 'file'):
                self.local_copy()
            elif self.task == ('file', 's3'):
                self.upload()
            elif self.task == ('s3', 'file'):
                self.download()
            elif self.task == ('s3', 's3'):
                self.remote_copy()
            else:
                raise InvalidSchemeException("Copy for URI Scheme %s to %s is not implemented" % self.task)
        except KeyNotFound:
            if self.dst.is_s3:
                try:
                    _ = self.dst.bucket
                except KeyNotFound:
                    raise  KeyNotFound("Error copying {} to {}: Destination bucket doesn't exist".format(self.src.uri, self.dst.uri))
            if not self.src.exists():
                raise KeyNotFound("Error copying {} to {}: Source doesn't exist".format(self.src.uri, self.dst.uri))
            else:
                raise KeyNotFound("Error copying {} to {}: Destination doesn't exist".format(self.src.uri, self.dst.uri))
        except IOError as e:
            import errno
            if e.errno == errno.ENOENT:
                raise KeyNotFound("Error copying {} to {}: Source doesn't exist".format(self.src.uri, self.dst.uri))
            else:
                raise S3Exception("Error copying {} to {}: {}".format(self.src.uri, self.dst.uri, e))
        except S3ResponseError as e:
            if e.status == 403:
                raise S3Exception("HTTP Error 403: Permission Denied on {}".format(" or ".join([x.uri for x in [self.src, self.dst] if x.is_s3])))
            else:
                raise

    def local_copy(self):
        import shutil
        shutil.copy(self.src.path, self.dst.path)

    def upload(self):
        if self.gzip:
            import gzip
            from baiji.util import tempfile
            with tempfile.NamedTemporaryFile() as compressed_src:
                with open(self.src.path, 'rb') as f:
                    with gzip.open(compressed_src.name, 'wb') as tf:
                        tf.writelines(f)
                self.src.path = compressed_src.name
                self.encoding = 'gzip'
                self._upload()
        else:
            self._upload()

    def _upload(self):
        self.file_size = os.path.getsize(self.src.path)
        if self.file_size > self.max_size:
            self.upload_multipart()
        else:
            self.upload_direct()

    def upload_multipart(self):
        import math
        from baiji.util.with_progressbar import FileTransferProgressbar
        with FileTransferProgressbar(supress=(not self.progress), maxval=self.file_size) as cb:
            mp = self.dst.bucket.initiate_multipart_upload(self.dst.remote_path, encrypt_key=self.encrypt, metadata=self.metadata)
            n_parts = int(math.ceil(float(self.file_size) / self.max_size))
            try:
                for ii in range(n_parts):
                    with open(self.src.path, 'r') as fp:
                        fp.seek(self.max_size*ii)
                        part_size = self.file_size - self.max_size*ii if ii+1 == n_parts else self.max_size
                        cb.minval = self.max_size*ii
                        num_cb = part_size / (1024*1024)
                        mp.upload_part_from_file(fp=fp, part_num=ii+1, size=part_size, cb=cb, num_cb=num_cb)
                mp.complete_upload()
            except:
                mp.cancel_upload()
                raise

    def upload_direct(self):
        import math
        from baiji.util.with_progressbar import FileTransferProgressbar
        key = self.dst.create()
        for k, v in self.metadata.items():
            key.set_metadata(k, v)
        with FileTransferProgressbar(supress=(not self.progress)) as cb:
            num_cb = max([10, int(math.ceil(float(self.file_size) / (1024*1024)))])
            key.set_contents_from_filename(self.src.path, cb=cb, policy=self.policy, encrypt_key=self.encrypt, num_cb=num_cb)

    def download(self):
        '''
        Download to local file

        If `validate` is set, check etags and retry once if not match.
        Raise TransientError when download is corrupted again after retry

        '''
        import shutil
        from baiji.util import tempfile
        from baiji.util.with_progressbar import FileTransferProgressbar
        # We create, close, and delete explicitly rather than using
        # a `with` block, since on windows we can't have a file open
        # twice by the same process.
        tf = tempfile.NamedTemporaryFile(delete=False)
        try:
            key = self.src.lookup(version_id=self.version_id)

            with FileTransferProgressbar(supress=(not self.progress)) as cb:
                key.get_contents_to_file(tf, cb=cb)
            tf.close()

            if self.validate:
                self.ensure_integrity(tf.name)

            # We only actually write to dst.path if the download succeeds and
            # if necessary is validated. This avoids leaving partially
            # downloaded files if something goes wrong.
            shutil.copy(tf.name, self.dst.path)

        except (get_transient_error_class(), KeyNotFound) as retryable_error:
            # Printed here so that papertrail can alert us when this occurs
            print retryable_error

            # retry once or raise
            if self.retries_made < self.retries_allowed:
                self._retries += 1
                self.download()
            else:
                raise
        finally:
            self.connection.rm(tf.name)

    def ensure_integrity(self, filename):
        '''
        Ensure integrity of downloaded file; raise TransientError if there's a mismatch
        '''
        if not self.connection.etag_matches(filename, self.src.etag()):
            raise get_transient_error_class()('Destinaton file for ({}) is corrupted, retry count {}'.format(self.src.uri, self.retries_made))

    def remote_copy(self):
        '''
        With copy_key, if metadata is None, it will be copied from the existing key
        '''
        headers = {}
        if self.policy:
            headers['x-amz-acl'] = self.policy
        key = self.src.lookup()
        meta = key.metadata
        meta['Content-Encoding'] = key.content_encoding
        meta['Content-Type'] = key.content_type
        meta = dict(meta.items() + self.metadata.items())
        self.dst.bucket.copy_key(
            self.dst.remote_path,
            self.src.bucket_name,
            self.src.remote_path,
            preserve_acl=self.preserve_acl,
            metadata=meta,
            headers=headers,
            encrypt_key=self.encrypt,
            src_version_id=self.version_id
        )

        if self.progress:
            print 'Copied %s to %s' % (self.src.uri, self.dst.uri)

    def prep_local_destination(self):
        from baiji.util.shutillib import mkdir_p
        mkdir_p(os.path.dirname(self.dst.path))


class MultifileCopyWorker(ParallelWorker):
    '''
    This is a pickleable worker used for parallel copy operations.
    '''
    def __init__(self, kwargs_for_cp):
        from baiji.connection import S3Connection
        self.connection = S3Connection(cache_buckets=True)
        self.kwargs_for_cp = kwargs_for_cp
        self.verbose = self.kwargs_for_cp.get('progress', False)
        if 'progress' in self.kwargs_for_cp:
            self.kwargs_for_cp['progress'] = False
        super(MultifileCopyWorker, self).__init__()

    def on_run(self, file_from, file_to):
        try:
            self.connection.cp(file_from, file_to, **self.kwargs_for_cp)
            if self.verbose:
                print "Finished transfering {} to {}".format(file_from, file_to)
        except KeyExists as e:
            # Note here that the correct behavior would probably be to roll back
            # if we encounter an error, but that's not practical, so we copy
            # what we can and show an error about the rest.
            print str(e)

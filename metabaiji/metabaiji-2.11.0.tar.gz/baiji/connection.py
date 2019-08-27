import os
from baiji import path
from baiji.exceptions import InvalidSchemeException, S3Exception, KeyNotFound, BucketNotFound, KeyExists

class S3Connection(object):
    def __init__(self, cache_buckets=False):
        self._connected = False
        self._conn = None
        self.cache_buckets = cache_buckets
        self._known_valid_buckets = set()

    @property
    def conn(self):
        from boto.s3 import connect_to_region
        from boto.s3.connection import OrdinaryCallingFormat
        from baiji.config import settings
        if not self._connected:
            self._conn = connect_to_region(
                settings.region,
                aws_access_key_id=settings.key,
                aws_secret_access_key=settings.secret,
                calling_format=OrdinaryCallingFormat(),
                suppress_consec_slashes=False)
            self._connected = True
        return self._conn

    def _bucket(self, name, cache_buckets=None):
        '''
        The call to `get_bucket` will make a HEAD request to S3 and raise S3ResponseError if the bucket doesn't exist.
        If we pass `validate=False` then it won't make the request, but it's behavior will be undefined if the bucket doesn't
        exist. So we don't want to not validate buckets in general, because that'd break things, but if we've seen the bucket
        before, then it's very likely that we'll see it again.

        We support an object wide cache_buckets, or we can pass cache_buckets just to this call, which will override the
        object wide value.
        '''
        from boto.s3.connection import S3ResponseError
        if cache_buckets is None:
            cache_buckets = self.cache_buckets
        try:
            if cache_buckets and name in self._known_valid_buckets:
                return self.conn.get_bucket(name, validate=False)
            else:
                bucket = self.conn.get_bucket(name) # this will raise S3ResponseError if the bucket isn't valid
                self._known_valid_buckets.add(name)
                return bucket
        except S3ResponseError as e:
            if e.status == 403:
                raise S3Exception("HTTP Error 403: Permission Denied on s3://{}/".format(name))
            elif e.status == 404:
                raise BucketNotFound('Bucket does not exist: {}'.format(name))
            else:
                raise

    def _lookup(self, bucket_name, key, cache_buckets=None, version_id=None):
        '''
        See _bucket for the details on cache_buckets
        '''
        from baiji.util.munging import _strip_initial_slashes
        from baiji.util.lookup import get_versioned_key_remote

        key = _strip_initial_slashes(key)

        try:
            bucket = self._bucket(bucket_name, cache_buckets=cache_buckets)
        except BucketNotFound:
            return None

        return get_versioned_key_remote(bucket, key, version_id=version_id)

    def cp(self, key_or_file_from, key_or_file_to, force=False, progress=False, policy=None, preserve_acl=False, encoding=None, encrypt=True, gzip=False, content_type=None, guess_content_type=False, metadata=None, skip=False, validate=True, max_size=None, version_id=None):
        """
        Copy file to or from AWS S3

        Both the from and to arguments can be either local paths or s3 urls (e.g. ``s3://bucketname/path/in/bucket``).

        If the target exists, the an exception is raised unless ``force=True`` is given.

        When copying from file to s3, you can optionally specify a canned acl policy,
        e.g. `policy='public-read'`. For possible values, see boto.s3.acl.CannedACLStrings.

        When copying from s3 to s3, you can specify preserve_acl=True to copy the
        existing ACL to the new file. With preserve_acl=False it will inherit the
        new bucket's policy.
        """
        from baiji.copy import S3CopyOperation

        op = S3CopyOperation(key_or_file_from, key_or_file_to, connection=self)
        op.progress = progress
        op.force = force
        op.policy = policy
        op.preserve_acl = preserve_acl
        op.encrypt = encrypt
        op.encoding = encoding
        op.gzip = gzip
        op.metadata = metadata
        op.skip = skip
        op.validate = validate
        op.max_size = max_size
        op.version_id = version_id

        if guess_content_type:
            op.guess_content_type()
        else:
            op.content_type = content_type

        op.execute()

    def cp_many(self, files_to_copy, parallel=False, **kwargs):
        '''
        files_to_copy should be a sequence of sequences on the form:
            [(src1, dst1), (src2, dst2),...]
        parallel is a bool. When True, files are copied in parallel.
        kwargs are passed on directly to s3.cp; see defaults there.
        '''
        if parallel:
            from baiji.util.parallel import parallel_for
            from baiji.copy import MultifileCopyWorker
            parallel_for(files_to_copy, MultifileCopyWorker, args=[kwargs], num_processes=12)
        else:
            for file_from, file_to in files_to_copy:
                try:
                    # Note here that the correct behavior would probably be to roll back
                    # if we encounter an error, but that's not practical, so we copy
                    # what we can and show an error about the rest.
                    self.cp(file_from, file_to, **kwargs)
                except KeyExists as e:
                    print str(e)

    def cp_r(self, dir_from, dir_to, parallel=False, **kwargs):
        '''
        kwargs are passed on directly to s3.cp; see defaults there.
        '''
        (from_scheme, _, from_path, _, _, _) = path.parse(dir_from)
        if from_scheme == 'file':
            files_to_copy = [(path.join(dir_from, f), path.join(dir_to, f))
                             for f in self.ls(dir_from, return_full_urls=False)]
        else:
            if from_path.endswith(path.sep):
                # Emulate `cp`, which copies the contents of the path.
                # Get path relative to from_path
                files_to_copy = [(f, path.join(dir_to, os.path.relpath(path.parse(f).path, from_path)))
                                 for f in self.ls(dir_from, return_full_urls=True) if not path.isdirlike(f)]
            else:
                # Get path relative to from_path's parent
                # Since from_path has no '/', we can get this with os.path.dirname()
                files_to_copy = [(f, path.join(dir_to, os.path.relpath(path.parse(f).path, os.path.dirname(from_path))))
                                 for f in self.ls(dir_from, return_full_urls=True) if not path.isdirlike(f)]

        if 'force' not in kwargs or not kwargs['force']:
            # we're not supposed to overwrite. Locally this is easy, since `exists` checks are cheap, but
            # on s3, it's more expensive, so we avoid it if possible:
            if path.isremote(dir_to):
                def common_prefix(a, b):
                    try:
                        ind = [x == y for x, y in zip(a, b)].index(False)
                    except ValueError:
                        return a
                    return a[:ind]
                destinations = [y for _, y in files_to_copy]
                prefix = reduce(common_prefix, destinations[1:], destinations[0])
                try:
                    # note that we can't use `exists` here, as it only works for full keys
                    self.ls(prefix).next()
                except StopIteration:
                    # There's nothing in the iterator, so there are no files to be found, so
                    # we set force for the copy so that we don't have to check each one:
                    kwargs['force'] = True
        self.cp_many(files_to_copy, parallel, **kwargs)


    def rm(self, key_or_file, version_id=None):
        '''
        Remove a key from AWS S3
        '''
        import shutil
        from baiji.util.munging import _strip_initial_slashes
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            if os.path.isdir(k.path):
                shutil.rmtree(k.path)
            elif os.path.exists(k.path):
                return os.remove(k.path)
            else:
                raise KeyNotFound("%s does not exist" % key_or_file)
        elif k.scheme == 's3':
            if not self.exists(key_or_file, version_id=version_id):
                raise KeyNotFound("%s does not exist" % key_or_file)
            return self._bucket(k.netloc).delete_key(_strip_initial_slashes(k.path), version_id=version_id)
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def rm_r(self, key_or_file, force=False, quiet=False):
        '''
        Prompts for confirmation on each file when force is False.

        Raises an exception when not using AWS.
        '''
        k = path.parse(key_or_file)
        if not k.scheme == 's3':
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)
        bucket = k.netloc
        keys_to_delete = self.ls(key_or_file)
        for key_to_delete in keys_to_delete:
            url = "s3://%s%s" % (bucket, key_to_delete)
            if not force:
                from baiji.util.console import confirm
                if not confirm("Remove %s" % url):
                    continue
            self.rm(url)
            if not quiet:
                print "[deleted] %s" % url

    def ls(self, s3prefix, return_full_urls=False, require_s3_scheme=False, shallow=False, followlinks=False, list_versions=False):
        '''
        List files on AWS S3
        prefix is given as an S3 url: ``s3://bucket-name/path/to/dir``.
        It will return all values in the bucket that have that prefix.

        Note that ``/dir/filename.ext`` is found by ``ls('s3://bucket-name/dir/fil')``; it's really a prefix and not a directory name.

        A local prefix generally is acceptable, but if require_s3_scheme
        is True, the prefix must be an s3 URL.

        If `shallow` is `True`, the key names are processed hierarchically
        using '/' as a delimiter, and only the immediate "children" are
        returned.

        '''
        import itertools
        k = path.parse(s3prefix)
        if k.scheme == 's3':
            prefix = k.path
            if prefix.startswith(path.sep):
                prefix = prefix[len(path.sep):]
            delimiter = shallow and path.sep or ''
            if return_full_urls:
                clean_paths = lambda x: "s3://" + k.netloc + path.sep + x.name
            else:
                clean_paths = lambda x: path.sep + x.name

            if list_versions:
                result_list_iterator = self._bucket(k.netloc).list_versions(prefix=prefix, delimiter=delimiter)
            else:
                result_list_iterator = self._bucket(k.netloc).list(prefix=prefix, delimiter=delimiter)

            return itertools.imap(clean_paths, result_list_iterator)
        elif k.scheme == 'file':
            if require_s3_scheme:
                raise InvalidSchemeException('URI should begin with s3://')
            paths = []
            remove = ''
            if not return_full_urls:
                remove = k.path
                if not remove.endswith(os.sep):
                    remove += os.sep
            for root, _, files in os.walk(k.path, followlinks=followlinks):
                for f in files:
                    # On Windows, results of os.abspath() and os.walk() have '\',
                    # so we replace them with '/'
                    paths.append(path.join(root, f).replace(remove, '').replace(os.sep, path.sep))
                if shallow:
                    break
            return paths
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def restore(self, key):
        from boto.s3.deletemarker import DeleteMarker
        k = path.parse(key)
        prefix = k.path
        if prefix.startswith(path.sep):
            prefix = prefix[len(path.sep):]
        versions = self._bucket(k.netloc).list_versions(prefix)
        delete_marker = [x for x in versions if x.name == prefix and isinstance(x, DeleteMarker) and x.is_latest]
        if delete_marker:
            self._bucket(k.netloc).delete_key(delete_marker[0].name, version_id=delete_marker[0].version_id)

    def glob(self, prefix, pattern):
        '''
        Given a path prefix and a pattern, iterate over matching paths.

        e.g.

        paths = list(s3.glob(
            prefix='s3://bodylabs-ants-go-marching/output/feet_on_floor/eff2a0e/',
            pattern='*_alignment.ply'
        ))

        '''
        import fnmatch
        import functools
        import itertools
        predicate = functools.partial(fnmatch.fnmatch, pat=prefix + pattern)
        listing = self.ls(prefix, return_full_urls=True)
        return itertools.ifilter(predicate, listing)

    def info(self, key_or_file):
        '''
        Get info about a file
        '''
        from datetime import datetime
        k = path.parse(key_or_file)
        result = {
            'uri': '%s://%s%s' % (k.scheme, k.netloc, k.path),
        }
        if k.scheme == 'file':
            if not os.path.exists(k.path):
                raise KeyNotFound("Error getting info on %s: File doesn't exist" % (key_or_file, ))
            stat = os.stat(k.path)
            result['size'] = stat.st_size
            result['last_modified'] = datetime.fromtimestamp(stat.st_mtime)
        elif k.scheme == 's3':
            remote_object = self._lookup(k.netloc, k.path)
            if remote_object is None:
                raise KeyNotFound("Error getting info on %s: Key doesn't exist" % (key_or_file, ))
            result['size'] = remote_object.size
            result['last_modified'] = datetime.strptime(remote_object.last_modified, "%a, %d %b %Y %H:%M:%S GMT")
            result['content_type'] = remote_object.content_type
            result['content_encoding'] = remote_object.content_encoding
            result['encrypted'] = bool(remote_object.encrypted)
            result['acl'] = remote_object.get_acl()
            result['owner'] = remote_object.owner
            result['version_id'] = remote_object.version_id
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)
        return result

    def exists(self, key_or_file, retries_allowed=3, version_id=None):
        '''
        Check if a file exists on AWS S3

        Returns a boolean.

        If the key is not found then we recheck up to `retries_allowed` times. We only do this
        on s3. We've had some observations of what appears to be eventual consistency, so this
        makes it a bit more reliable. This does slow down the call in the case where the key
        does not exist.

        On a relatively slow, high latency connection a test of 100 tests retreiving a
        non-existant file gives:

        With retries_allowed=1: median=457.587 ms, mean=707.12387 ms
        With retries_allowed=3: median=722.969 ms, mean=1185.86299 ms
        with retries_allowed=10: median=2489.767 ms, mean=2995.34233 ms
        With retries_allowed=100: median=24694.0815 ms, mean=26754.64137 ms

        So assume that letting retries_allowed=3 will cost you a bit less than double the time.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            return os.path.exists(k.path)
        elif k.scheme == 's3':
            retry_attempts = 0
            while retry_attempts < retries_allowed:
                key = self._lookup(k.netloc, k.path, cache_buckets=True, version_id=version_id)
                if key:
                    if retry_attempts > 0: # only if we find it after failing at least once
                        import warnings
                        from baiji.exceptions import EventualConsistencyWarning
                        warnings.warn("S3 is behaving in an eventually consistent way in s3.exists({}) -- it took {} attempts to locate the key".format(key_or_file, retry_attempts+1), EventualConsistencyWarning)
                    return True
                retry_attempts += 1
            return False
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def size(self, key_or_file, version_id=None):
        '''
        Return the size of a file. If it's on s3, don't download it.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            return os.path.getsize(k.path)
        elif k.scheme == 's3':
            k = self._lookup(k.netloc, k.path, version_id=version_id)
            if k is None:
                raise KeyNotFound("s3://%s/%s not found on s3" % (k.netloc, k.path))
            return k.size
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def _get_etag(self, netloc, remote_path):
        k = self._lookup(netloc, remote_path)
        if k is None:
            raise KeyNotFound("s3://%s/%s not found on s3" % (netloc, remote_path))
        return k.etag.strip("\"") # because s3 seriously gives the md5sum back wrapped in an extra set of double quotes...

    def _build_etag(self, local_path, n_parts, part_size):
        '''
        When a file has been uploaded to s3 as a multipart upload, the etag is no
        longer a simple md5 hash. What happens is s3 calculates md5 hashes of each
        of the parts as they are uploaded and then when the final "complete upload"
        step is run, the individual md5 hashes are concatenated and put through a
        final round of md5. Then the number of parts is appended to the hash with
        a -, in the form `HASH-N`. The algorithm is undocumented (and Amazon has
        changed it without notice in the past), but more details can be found here:
        http://stackoverflow.com/questions/12186993/what-is-the-algorithm-to-compute-the-amazon-s3-etag-for-a-file-larger-than-5gb
        '''
        import hashlib
        import struct
        from baiji.util.md5 import md5_for_file
        starts = [ii*part_size for ii in range(n_parts)]
        ends = [(ii+1)*part_size for ii in range(n_parts)]
        ends[-1] = None
        hashes = [md5_for_file(local_path, start=start, end=end) for start, end in zip(starts, ends)]
        md5_digester = hashlib.md5()
        for h in hashes:
            md5_digester.update(struct.pack("!16B", *[int(h[x:x+2], 16) for x in range(0, len(h), 2)]))
        return md5_digester.hexdigest() + "-%d" % n_parts

    def etag_matches(self, key_or_file, other_etag):
        import math
        from baiji.copy import S3_MAX_UPLOAD_SIZE
        k = path.parse(key_or_file)
        # print "***", key_or_file, other_etag
        if "-" not in other_etag or k.scheme == 's3':
            return self.etag(key_or_file) == other_etag
        else: # This is the case where the key was uploaded multipart and has a `md5-n_parts` type etag
            n_parts = int(other_etag.split("-")[1])
            file_size = os.path.getsize(k.path)
            # There are a number of possible part sizes that could produce any given
            # number of parts. The most likely and only ones we've seen so far are
            # these, but we might someday need to try others, which might require
            # exhaustively searching the possibilities....

            # (n_parts-1) * part_size >= file_size >= n_parts * part_size
            min_part_size = int(math.ceil(float(file_size)/n_parts))
            max_part_size = file_size / (n_parts-1)
            # print "  - min part size {} gives last block size of {}".format(min_part_size, file_size - min_part_size*(n_parts-1))
            # print "  - max part size {} gives last block size of {}".format(max_part_size, file_size - max_part_size*(n_parts-1))
            possible_part_sizes = [
                S3_MAX_UPLOAD_SIZE, # what we do
                file_size/n_parts, # seen this from third party uploaders
                min_part_size, # just in case
                max_part_size, # seen this from third party uploaders
                1024*1024*8, # seen this from third party uploaders
                1024*1024*5, # the minimum s3 will allow
            ]
            # print "  - {} parts, file size {} bytes".format(n_parts, file_size)
            # print "  - possible_part_sizes:", possible_part_sizes
            possible_part_sizes = set([part_size for part_size in possible_part_sizes if part_size <= max_part_size and part_size >= 1024*1024*5])
            # print "  - possible_part_sizes:", possible_part_sizes
            if not possible_part_sizes:
                return False
            for part_size in possible_part_sizes:
                # print "  -", part_size, self._build_etag(k.path, n_parts, part_size)
                if self._build_etag(k.path, n_parts, part_size) == other_etag:
                    return True
            return False

    def etag(self, key_or_file):
        '''
        Return the s3 etag of the file. For single part uploads (for us, files less than 5gb) this is the same as md5.
        '''
        from baiji.copy import S3_MAX_UPLOAD_SIZE
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            import math
            from baiji.util.md5 import md5_for_file
            file_size = os.path.getsize(k.path)
            if file_size > S3_MAX_UPLOAD_SIZE:
                n_parts = int(math.ceil(float(file_size) / S3_MAX_UPLOAD_SIZE))
                return self._build_etag(k.path, n_parts, S3_MAX_UPLOAD_SIZE)
            else:
                return md5_for_file(k.path)
        elif k.scheme == 's3':
            return self._get_etag(k.netloc, k.path)
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def md5(self, key_or_file):
        '''
        Return the MD5 checksum of a file. If it's on s3, don't download it.
        '''
        k = path.parse(key_or_file)
        if k.scheme == 'file':
            from baiji.util.md5 import md5_for_file
            return md5_for_file(k.path)
        elif k.scheme == 's3':
            res = self._get_etag(k.netloc, k.path)
            if "-" in res:
                raise ValueError("md5 hashes not available from s3 for files that were uploaded as multipart (if over 5gb, there's no hope; if under, try copying it to itself to have S3 reset the etag)")
            return res
        else:
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)

    def encrypt_at_rest(self, key):
        '''
        This method takes a key on s3 and encrypts it.
        Note that calling this method on a local file is an error
        and that calling it on an s3 key that is already encrypted,
        while allowed, is a no-op.
        '''
        k = path.parse(key)
        if k.scheme != 's3':
            raise InvalidSchemeException("URI Scheme %s is not implemented" % k.scheme)
        remote_object = self._lookup(k.netloc, k.path)
        if remote_object is None:
            raise KeyNotFound("Error encrypting %s: Key doesn't exist" % (key, ))
        if not bool(remote_object.encrypted):
            bucket = self._bucket(k.netloc)
            src = k.path
            if src.startswith(path.sep):
                src = src[len(path.sep):] # NB: copy_key is failing with absolute src keys...
            bucket.copy_key(src, k.netloc, src, preserve_acl=True, metadata=None, encrypt_key=True)

    def mv(self, key_or_file_from, key_or_file_to, **kwargs):
        """
        Move file to or from AWS S3

        Both the from and to arguments can be either local paths or s3 urls (e.g. ``s3://bucketname/path/in/bucket``).

        If the target exists, the an exception is raised unless ``force=True`` is given.
        kwargs are passed directly on to s3.cp; see there for defaults.
        """
        self.cp(key_or_file_from, key_or_file_to, **kwargs)
        self.rm(key_or_file_from)

    def touch(self, key, encrypt=True):
        """
        Touch a local file or a path on s3

        Locally, this is analagous to the unix touch command

        On s3, it creates an empty file if there is not one there already,
        but does not change the timestamps (not possible to do without
        actually moving the file)
        """
        if path.islocal(key):
            filename = path.parse(key).path
            with open(filename, 'a'):
                os.utime(filename, None)
        else:
            # The replace=False here means that we only take action if
            # the file doesn't exist, so we don't accidentally truncate
            # files when we just mean to be touching them
            self.put_string(key, '', encrypt=encrypt, replace=False)

    def sync_file(self, src, dst, update=True, delete=False, progress=False, policy=None, encoding=None, encrypt=True, guess_content_type=False):
        '''
        Sync a file from src to dst.

        update: When True, update dst if it exists but contents do not match.
        delete: When True, remove dst if src does not exist. When False, raise
          an error if src does not exist.

        As this function is a file by file sync, not applicable to directories
        nor recursive, src being a directory is best treated as mkdir_p(dst).
        '''
        from baiji.util.console import create_conditional_print
        print_verbose = create_conditional_print(progress)

        if path.isdirlike(src):
            print_verbose('{} is a directory'.format(src))
            if path.islocal(dst): # for remote paths, don't bother creating dirs; they don't really exist.
                from baiji.util.shutillib import mkdir_p
                mkdir_p(dst)
            return

        src_exists = self.exists(src)
        if not delete and not src_exists:
            raise KeyNotFound(
                "Error syncing {} to {}: Source doesn't exist".format(src, dst))

        dst_exists = self.exists(dst)

        needs_delete = dst_exists and not src_exists
        needs_fresh_copy = src_exists and not dst_exists
        needs_update = dst_exists and src_exists and self.etag(src) != self.etag(dst)

        if not needs_delete and not needs_fresh_copy and not needs_update:
            print_verbose('{} is up to date'.format(dst))
            return

        # At this point, exactly one of these should be true.
        assert needs_delete ^ needs_fresh_copy ^ needs_update

        if needs_fresh_copy:
            print_verbose('copying {} to {}'.format(src, dst))
            self.cp(src, dst, force=False, progress=progress, policy=policy, encoding=encoding, encrypt=encrypt, guess_content_type=guess_content_type)
        elif needs_update:
            print_verbose('file is out of date: {}'.format(dst))
            if update:
                print_verbose('copying {} to {}'.format(src, dst))
                self.cp(src, dst, force=True, progress=progress, policy=policy, encoding=encoding, encrypt=encrypt, guess_content_type=guess_content_type)
        elif needs_delete:
            print_verbose('source file does not exist: {}'.format(src))
            if delete:
                print_verbose('removing {}'.format(dst))
                self.rm(dst)

    def sync(self, key_or_dir_from, key_or_dir_to, followlinks=True, do_not_delete=None, progress=False, policy=None, encoding=None, encrypt=True, guess_content_type=False):
        '''
        Sync a directory of files.

        Note these src and dst paths must be directories. Use `s3.sync_file`
        for files.

        do_not_delete: Paths not to delete during syncing, useful for syncing root
          content in a bucket when other apps are responsible for filling in
          subfolders.

        '''
        def clean_path(key_or_dir):
            if path.islocal(key_or_dir) and not os.path.isdir(key_or_dir):
                raise ValueError("s3 sync requires directories")
            if path.islocal(key_or_dir):
                key_or_dir = os.path.abspath(key_or_dir)
            if not key_or_dir.endswith('/'):
                key_or_dir += '/'
            return key_or_dir

        key_or_dir_from = clean_path(key_or_dir_from)
        key_or_dir_to = clean_path(key_or_dir_to)

        src_files = [x.replace(key_or_dir_from, '') for x in self.ls(key_or_dir_from, return_full_urls=True, followlinks=followlinks)]
        dst_files = [x.replace(key_or_dir_to, '') for x in self.ls(key_or_dir_to, return_full_urls=True, followlinks=followlinks)]
        for f in src_files:
            src = key_or_dir_from + f
            dst = key_or_dir_to + f
            self.sync_file(src, dst, progress=progress, policy=policy, encoding=encoding, encrypt=encrypt, guess_content_type=guess_content_type)

        do_not_delete = [] if do_not_delete is None else do_not_delete
        do_not_delete = [x if x.endswith('/') else x + '/' for x in do_not_delete]
        for f in set(dst_files) - set(src_files):
            removed_file = key_or_dir_to + f
            if any([f.startswith(x) for x in do_not_delete]):
                if progress:
                    print "leaving alone", removed_file
            else:
                if progress:
                    print "removing", removed_file
                self.rm(removed_file)

    def get_url(self, key, ttl):
        """
        Get a temporary https url for a file on AWS S3

        Returns the url as a string.
        The url will timeout and return an error after ``ttl`` seconds.
        """
        k = path.parse(key)
        return self._lookup(k.netloc, k.path).generate_url(ttl)

    def put_string(self, key, s, encrypt=True, replace=True):
        '''
        Save string ``s`` to S3 as ``key``.

        If ``replace=True``, this will overwrite an existing key.
        If ``replace=false``, this will be a no-op when the key already exists.

        '''
        from boto.s3.key import Key
        from baiji.util.munging import _strip_initial_slashes
        key = path.parse(key)
        b = self._bucket(key.netloc)
        k = Key(b)
        k.key = _strip_initial_slashes(key.path)
        k.set_contents_from_string(s, encrypt_key=encrypt, replace=replace)

    def get_string(self, key):
        '''
        Get string stored in S3 ``key``.
        '''
        k = path.parse(key)
        return self._lookup(k.netloc, k.path).get_contents_as_string()

    def open(self, key, mode='rb'): # pylint: disable=redefined-builtin
        '''
        Acts like open(key, mode), opening a file.

        If the file is on S3, it is downloaded and a NamedTemporaryFile is returned.

        The caller is responsible for closing the file descriptor, please try to
        use it in a with block.

        Like os.open, after stripping 'U' from the mode, the first character must
        be 'r' or 'w'. open also accepts 'x' for exclusive creation: it raises an
        exception if the file already exists. This is meant as a convenience and
        sanity check when you know the original file isn't supposed to exist.

        Note that 'x' is not suitable for preventing concurrent creation. This is
        due to the "eventually consistent" nature of s3, and also the CachedFile
        design. If two processes simultaneously write to the same file, there's a
        race condition. One or both will appear to succeed, and one will win out.
        Using 'x' doesn't -- can't -- prevent this.

        Raises s3.KeyNotFound when attempting to open a local or remote file that
        doesn't exist, s3.KeyExists when attempting exclusive create on an
        existing file or key, ValueError for an invalid key, and IOError for an
        underlying local file-system failure.

        '''
        from baiji.cached_file import CachedFile
        return CachedFile(key, mode, connection=self)

    def list_buckets(self):
        '''
        List all the buckets availiable on AWS S3 for the credentialed account.
        '''
        return [x.name for x in self.conn.get_all_buckets()]

    def bucket_info(self, name):
        '''
        Get info about a bucket
        '''
        bucket = self._bucket(name)
        def safe_get(method):
            from boto import exception
            try:
                return getattr(bucket, method)()
            except exception.S3ResponseError:
                return None
        versioning_status = safe_get('get_versioning_status')
        if versioning_status is not None and 'Versioning' in versioning_status:
            versioning_status = versioning_status['Versioning']
        else:
            versioning_status = "Not Versioned"
        return {
            'name': name,
            'lifecycle': safe_get('get_lifecycle_config'),
            'cors': safe_get('get_cors'),
            'location': safe_get('get_location'),
            'logging_status': safe_get('get_logging_status'),
            'policy': safe_get('get_policy'),
            'versioning_status': versioning_status,
            'website_configuration': safe_get('get_website_configuration'),
            'website_endpoint': safe_get('get_website_endpoint'),
        }

    def create_bucket(self, name, versioned=True):
        bucket = self.conn.create_bucket(name)
        if versioned:
            self.enable_versioning(name)
        return bucket

    def enable_versioning(self, bucket):
        self._bucket(bucket).configure_versioning(True)

    def disable_versioning(self, bucket):
        self._bucket(bucket).configure_versioning(False)

"""
Tools for interacting with Amazon S3.

This module seeks to be higher-level and easier to use than the boto library
provided by Amazon. It abstracts away whether you are writing to S3 or to a
local file, which is important for running code locally, or in an environment
where there is no connection to S3. It also adds some functionality that we
like, such as progress bars, "exclusive create", and context handlers (`with`)
for reading and writing.

The functionality provided by boto is relatively low level: it allows, for
example, setting an S3 key's contents from a string or local file, or pulling
a file from S3 into a local file.

"""
from baiji.connection import S3Connection
import baiji.path as path
from baiji.exceptions import InvalidSchemeException, S3Exception, KeyNotFound, BucketNotFound, KeyExists # just making them available pylint: disable=unused-import

sep = path.sep # backwards compatibility

# The following convenience functions create a connection to s3 and execute the command

def cp(*args, **kwargs):
    return S3Connection().cp(*args, **kwargs)

def cp_r(*args, **kwargs):
    return S3Connection().cp_r(*args, **kwargs)

def cp_many(*args, **kwargs):
    return S3Connection().cp_many(*args, **kwargs)

def rm(*args, **kwargs):
    return S3Connection().rm(*args, **kwargs)

def rm_r(*args, **kwargs):
    return S3Connection().rm_r(*args, **kwargs)

def ls(*args, **kwargs):
    return S3Connection().ls(*args, **kwargs)

def glob(*args, **kwargs):
    return S3Connection().glob(*args, **kwargs)

def info(*args, **kwargs):
    return S3Connection().info(*args, **kwargs)

def restore(*args, **kwargs):
    return S3Connection().restore(*args, **kwargs)

def exists(*args, **kwargs):
    return S3Connection().exists(*args, **kwargs)

def size(*args, **kwargs):
    return S3Connection().size(*args, **kwargs)

def etag(*args, **kwargs):
    return S3Connection().etag(*args, **kwargs)

def etag_matches(*args, **kwargs):
    return S3Connection().etag_matches(*args, **kwargs)

def md5(*args, **kwargs):
    return S3Connection().md5(*args, **kwargs)

def encrypt_at_rest(*args, **kwargs):
    return S3Connection().encrypt_at_rest(*args, **kwargs)

def mv(*args, **kwargs):
    return S3Connection().mv(*args, **kwargs)

def touch(*args, **kwargs):
    return S3Connection().touch(*args, **kwargs)

def sync_file(*args, **kwargs):
    return S3Connection().sync_file(*args, **kwargs)

def sync(*args, **kwargs):
    return S3Connection().sync(*args, **kwargs)

def get_url(*args, **kwargs):
    return S3Connection().get_url(*args, **kwargs)

def put_string(*args, **kwargs):
    return S3Connection().put_string(*args, **kwargs)

def get_string(*args, **kwargs):
    return S3Connection().get_string(*args, **kwargs)

def list_buckets(*args, **kwargs):
    return S3Connection().list_buckets(*args, **kwargs)

def bucket_info(*args, **kwargs):
    return S3Connection().bucket_info(*args, **kwargs)

def create_bucket(*args, **kwargs):
    return S3Connection().create_bucket(*args, **kwargs)

def enable_versioning(*args, **kwargs):
    return S3Connection().enable_versioning(*args, **kwargs)

def disable_versioning(*args, **kwargs):
    return S3Connection().disable_versioning(*args, **kwargs)

def open(key, mode='rb', version_id=None): # pylint: disable=redefined-builtin
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

    version_id: comes handy when opening remote versioned files. no-op otherwise

    '''
    from baiji.cached_file import CachedFile
    return CachedFile(key, mode, version_id=version_id)

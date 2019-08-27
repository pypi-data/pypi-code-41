import os

# Path components in our s3 URIs are separated by slashes. Constant included not
# because it should ever change, but for semantic use in code. Remember that os.sep
# is '/' on MacOS and Linux and '\' on Windows.
sep = '/'

def parse(s):
    '''
    Parse a path given as a url. Accepts strings of the form:

       s3://bucket-name/path/to/key
       file:///path/to/file
       /absolution/path/to/file
       relative/path/to/file
       ~/path/from/home/dir/to/file

       To avoid surprises, s3:// and file:// URLs should not
       include ;, ? or #. You should URL-encode such paths.

    Return value is a ParseResult; one of the following:

       ('s3', bucketname, valid_s3_key, ...)
       ('file', '', absolute_path_for_current_filesystem, ...)

    '''
    import re
    from urlparse import urlparse, ParseResult

    if not isinstance(s, basestring):
        raise ValueError("An S3 path must be a string, got %s" % s.__class__.__name__)

    is_windows_path = (len(s) >= 2 and s[1] == ':')
    if is_windows_path:
        scheme, netloc, s3path = 'file', '', s
    else:
        scheme, netloc, s3path, params, query, fragment = urlparse(s)
        if any([params, query, fragment]):
            raise ValueError("Invalid URI: %s" % s)
        if any(char in ';?#' for char in s):
            raise ValueError("Invalid URI: %s" % s)
        try:
            s3path.encode('UTF-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            raise ValueError("Invalid URI (bad unicode): %s" % s)
            # If somehow something ever gets uploaded with binary in the
            # key, this seems to be the only way to fix it:
            # `s3cmd fixbucket s3://bodylabs-korper-assets`
    if re.match(r'/\w:', s3path): # urlparse, given file:///C:\foo parses us to /C:\foo, so on reconstruction (on windows) we get C:\C:\foo.
        s3path = s3path[1:]
        is_windows_path = True
    if scheme == '':
        scheme = 'file'
    if scheme == 'file' and not is_windows_path:
        if s3path.endswith(os.sep) or s3path.endswith('/'):
            # os.path.abspath strips the trailing '/' so we need to put it back
            s3path = os.path.join(os.path.abspath(os.path.expanduser(s3path)), '')
        else:
            s3path = os.path.abspath(os.path.expanduser(s3path))
    if scheme == 's3' and netloc == '':
        raise ValueError('s3 urls must specify the bucket')
    return ParseResult(scheme, netloc, s3path, params=None, query=None, fragment=None) # pylint: disable=too-many-function-args,unexpected-keyword-arg

def islocal(s):
    '''
    Check if a path is local. Just parses and checks format, _does not_ check for existence of the file.
    '''
    return parse(s).scheme == 'file'

def isremote(s):
    '''
    Check if a path is on S3. Just parses and checks format, _does not_ check for existence of the file.
    '''
    return parse(s).scheme == 's3'

def gettmpdir(prefix='tmp/', suffix='', bucket='bodylabs-temp', uuid_generator=None): # pylint: disable=redefined-outer-name
    '''
    Make a directory on S3 with a known unique name. The prefix for the directory will be
    ``s3://<bucket>/<prefix><UUID><suffix>/``

    Note that there _is_ a race condition in this code; if two clients happen to be trying to create a tmpdir and
    somehow come up with the same uuid exactly simultaniously, they could both get the same dir. But in practice this
    is sufficiently one in a billion that we'll not worry about it for now.
    '''
    from boto.s3.key import Key
    from baiji.connection import S3Connection
    if uuid_generator is None:
        from uuid import uuid4 as uuid_generator # pragma: no cover

    #s3.ls and s3.path.parse generated one with leading slash so remove it in case
    prefix = prefix.lstrip('/')
    b = S3Connection()._bucket(bucket) # pylint: disable=protected-access
    done = False
    while not done:
        tmppath = "%s%s%s" % (prefix, uuid_generator(), suffix)
        existin_files_at_tmppath = [x for x in b.list(prefix=tmppath)]
        if not existin_files_at_tmppath:
            k = Key(b)
            k.key = "%s/.tempdir" % (tmppath)
            k.set_contents_from_string('')
            done = True
    return "s3://%s/%s/" % (bucket, tmppath)

def join(base, *additions):
    '''
    Extends os.path.join so work with s3:// and file:// urls

    This inherits a quirk of os.path.join: if 'addition' is
    an absolute path, path components of base are thrown away.

    'addition' must be an absolute or relative path, not
    a URL.

    `base` and `addition` can use any path separator, but the
    result will always be normalized to os.sep.

    '''
    from urlparse import urlparse, urljoin, ParseResult

    addition = sep.join(additions)

    (scheme, netloc, _, params, query, fragment) = urlparse(addition)
    if any([scheme, netloc, params, query, fragment]):
        raise ValueError('Addition must be an absolute or relative path, not a URL')

    if islocal(base):
        return os.path.join(parse(base).path, addition.replace(sep, os.sep))
    k = parse(base)

    # Call urljoin instead of os.path.join, since it uses '/' instead of
    # os.sep, which is '\' on Windows.
    #
    # Given disparity between os.path.join and urljoin, we prefer the
    # behavior of os.path.join:
    #
    #   >>> os.path.join('foo/bar', 'baz')
    #   'foo/bar/baz'
    #   >>> urlparse.urljoin('foo/bar', 'baz')
    #   'foo/baz'
    #
    # So we add a trailing slash if there is none
    if k.path.endswith(sep):
        s3path = urljoin(k.path, addition)
    else:
        s3path = urljoin(k.path + sep, addition)

    return ParseResult(k.scheme, k.netloc, s3path, k.params, k.query, k.fragment).geturl() # pylint: disable=too-many-function-args,unexpected-keyword-arg

def basename(key):
    '''
    Finds the basename of a file on s3 or local. For local, it's equivalent to os.path.basename
    '''
    k = parse(key)
    return os.path.basename(k.path)

def dirname(key):
    '''
    Finds the dirname of a file on s3 or local. For local, it's equivalent to os.path.dirname
    '''
    # Oddly enough, os.path.dirname works correctly on URIs...
    return os.path.dirname(key)

def isdirlike(key):
    """
    Returns True for any key that is either a local, existing directory or
    ends with `sep` or `os.sep`. Otherwise returns False.
    This preserves the old `isdir` behavior.
    """
    k = parse(key)
    if islocal(key) and os.path.isdir(k.path):
        return True
    else:
        return k.path.endswith(sep) or k.path.endswith(os.sep)

def isdir(key):
    '''
    Return true if key is directory-ish. That is, it ends with a path
    separator, or is a local directory that actually exists.
    On S3 a "directory" is considered to exist if one or more files exist
    that have the "directory" (ending with sep) as a prefix.
    '''
    from baiji.connection import S3Connection
    from baiji.exceptions import InvalidSchemeException

    k = parse(key)
    if islocal(key): #This really only ensures that scheme == 'file'
        return os.path.isdir(k.path)
    if isremote(key): # scheme == 'S3'
        if not k.path.endswith(sep):
            k = parse(key + sep)
        try:
            next(S3Connection().ls(k.geturl()))
            return True
        except StopIteration:
            return False
    else:
        raise InvalidSchemeException("URI Scheme {} is not implemented".format(k.scheme))

def isfile(key):
    '''
    Return true if key is file; local or s3.
    '''
    from baiji.connection import S3Connection
    from baiji.exceptions import InvalidSchemeException
    k = parse(key)
    if islocal(key): #This really only ensures that scheme == 'file'
        return os.path.isfile(k.path)
    if isremote(key): # scheme == 'S3'
        # exists currently only works for files on s3 because
        # directories don't exist on s3, only files.
        return S3Connection().exists(key)
    else:
        raise InvalidSchemeException("URI Scheme {} is not implemented".format(k.scheme))

def bucket(key):
    '''
    Extracts the bucket from a key.
    '''
    k = parse(key)
    return k.netloc

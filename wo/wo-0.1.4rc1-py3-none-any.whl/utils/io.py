import hashlib
import urllib.parse

def md5_file(filename):
    """ 
    Calculate md5 hash of file contents. 

    Parameters
    ----------
    filename: str
        Path to a file of which md5 should be calculated.
    
    Returns
    --------
    hash_md5: str
        MD5 hash of the file. 
    """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def md5_files(filenames):
    """ 
    Calculate md5 hash of each files' contents. 

    Parameters
    ----------
    filename: str
        Path to a file of which md5 should be calculated.
    
    Returns
    --------
    hash_md5: str
        MD5 hash of the file. 
    """
    hash_md5 = hashlib.md5()
    for filename in filenames: 
        with open(filename, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    return hash_md5.hexdigest()


def md5_string(string):
    """ 
    Calculate md5 hash of the given string 

    Parameters
    ----------
    string: str
        String of which md5 should be calculated.
    
    Returns
    --------
    hash_md5: str
        MD5 hash of the given string. 
    """
    return hashlib.md5(string.encode("utf-8")).hexdigest()


def parse_uri(uri):
    """
    Parse given URI into subparts.

    Parameters
    ----–-----
    uri: str
        URI, containing scheme, bucket name and possibly path.
    
    Returns
    -------
    tuple: (scheme, bucket_name, key)
        A tuple, which contains bucket scheme (either s3 or gs), a bucket name 
        and key/prefix representing relative path in the bucket.
    """
    result = urllib.parse.urlparse(uri)
    if not result.scheme:
        raise ValueError("URI must contain scheme and a bucket name")
    if result.scheme not in ('s3', 'gs'):
        raise ValueError("Only s3 and gs are supported")
    return result.scheme, result.netloc, result.path.strip("/")


def parse_bucket(uri, with_scheme=False):
    """
    Parse given URI and retrieve bucket name.

    Parameters
    ----------
    uri: str
        URI, containing scheme, bucket name and possibly path.
    
    Returns
    -------
    str
        Bucket name, retrieved from URI.
    """
    result = urllib.parse.urlparse(uri)
    if with_scheme:
        return f"{result.scheme}://{result.netloc}"
    return result.netloc


def parse_path(uri):
    """
    Parse given URI and retrieve relative path.

    Parameters
    ----------
    uri: str
        URI, containing scheme, bucket name and possibly path.
    
    Returns
    -------
    str
        Relative path, retrieved from URI.
    """
    return urllib.parse.urlparse(uri).path.strip("/")
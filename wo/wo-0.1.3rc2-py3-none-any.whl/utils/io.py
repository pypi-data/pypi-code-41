import hashlib


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
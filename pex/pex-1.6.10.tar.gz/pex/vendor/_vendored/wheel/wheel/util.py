"""Utility functions."""

import base64
import hashlib
import json
import os
import sys

__all__ = ['urlsafe_b64encode', 'urlsafe_b64decode', 'utf8',
           'to_json', 'from_json', 'matches_requirement']


# For encoding ascii back and forth between bytestrings, as is repeatedly
# necessary in JSON-based crypto under Python 3
if sys.version_info[0] < 3:
    text_type = unicode  # noqa: F821

    def native(s, encoding='ascii'):
        return s
else:
    text_type = str

    def native(s, encoding='ascii'):
        if isinstance(s, bytes):
            return s.decode(encoding)
        return s


def urlsafe_b64encode(data):
    """urlsafe_b64encode without padding"""
    return base64.urlsafe_b64encode(data).rstrip(binary('='))


def urlsafe_b64decode(data):
    """urlsafe_b64decode without padding"""
    pad = b'=' * (4 - (len(data) & 3))
    return base64.urlsafe_b64decode(data + pad)


def to_json(o):
    """Convert given data to JSON."""
    return json.dumps(o, sort_keys=True)


def from_json(j):
    """Decode a JSON payload."""
    return json.loads(j)


def open_for_csv(name, mode):
    if sys.version_info[0] < 3:
        kwargs = {}
        mode += 'b'
    else:
        kwargs = {'newline': '', 'encoding': 'utf-8'}

    return open(name, mode, **kwargs)


def utf8(data):
    """Utf-8 encode data."""
    if isinstance(data, text_type):
        return data.encode('utf-8')
    return data


def binary(s):
    if isinstance(s, text_type):
        return s.encode('ascii')
    return s


class HashingFile(object):
    def __init__(self, path, mode, hashtype='sha256'):
        self.fd = open(path, mode)
        self.hashtype = hashtype
        self.hash = hashlib.new(hashtype)
        self.length = 0

    def write(self, data):
        self.hash.update(data)
        self.length += len(data)
        self.fd.write(data)

    def close(self):
        self.fd.close()

    def digest(self):
        if self.hashtype == 'md5':
            return self.hash.hexdigest()
        digest = self.hash.digest()
        return self.hashtype + '=' + native(urlsafe_b64encode(digest))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fd.close()


if sys.platform == 'win32':
    import ctypes.wintypes
    # CSIDL_APPDATA for reference - not used here for compatibility with
    # dirspec, which uses LOCAL_APPDATA and COMMON_APPDATA in that order
    csidl = {'CSIDL_APPDATA': 26, 'CSIDL_LOCAL_APPDATA': 28, 'CSIDL_COMMON_APPDATA': 35}

    def get_path(name):
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(0, csidl[name], 0, SHGFP_TYPE_CURRENT, buf)
        return buf.value

    def save_config_path(*resource):
        appdata = get_path("CSIDL_LOCAL_APPDATA")
        path = os.path.join(appdata, *resource)
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def load_config_paths(*resource):
        ids = ["CSIDL_LOCAL_APPDATA", "CSIDL_COMMON_APPDATA"]
        for id in ids:
            base = get_path(id)
            path = os.path.join(base, *resource)
            if os.path.exists(path):
                yield path
else:
    def save_config_path(*resource):
        import xdg.BaseDirectory
        return xdg.BaseDirectory.save_config_path(*resource)

    def load_config_paths(*resource):
        import xdg.BaseDirectory
        return xdg.BaseDirectory.load_config_paths(*resource)


def matches_requirement(req, wheels):
    """List of wheels matching a requirement.

    :param req: The requirement to satisfy
    :param wheels: List of wheels to search.
    """
    try:
        if "__PEX_UNVENDORED__" in __import__("os").environ:
          from pkg_resources import Distribution, Requirement  # vendor:skip
        else:
          from pex.third_party.pkg_resources import Distribution, Requirement

    except ImportError:
        raise RuntimeError("Cannot use requirements without pkg_resources")

    req = Requirement.parse(req)

    selected = []
    for wf in wheels:
        f = wf.parsed_filename
        dist = Distribution(project_name=f.group("name"), version=f.group("ver"))
        if dist in req:
            selected.append(wf)
    return selected

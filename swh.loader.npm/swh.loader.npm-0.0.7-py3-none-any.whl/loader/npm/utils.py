# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import json
import re

from codecs import BOM_UTF8

import chardet

_EMPTY_AUTHOR = {'fullname': b'', 'name': None, 'email': None}

# https://github.com/jonschlinkert/author-regex
_author_regexp = r'([^<(]+?)?[ \t]*(?:<([^>(]+?)>)?[ \t]*(?:\(([^)]+?)\)|$)'


def parse_npm_package_author(author_str):
    """
    Parse npm package author string.

    It works with a flexible range of formats, as detailed below::

        name
        name <email> (url)
        name <email>(url)
        name<email> (url)
        name<email>(url)
        name (url) <email>
        name (url)<email>
        name(url) <email>
        name(url)<email>
        name (url)
        name(url)
        name <email>
        name<email>
        <email> (url)
        <email>(url)
        (url) <email>
        (url)<email>
        <email>
        (url)

    Args:
        author_str (str): input author string

    Returns:
        dict: A dict that may contain the following keys:
            * name
            * email
            * url

    """
    author = {}
    matches = re.findall(_author_regexp,
                         author_str.replace('<>', '').replace('()', ''),
                         re.M)
    for match in matches:
        if match[0].strip():
            author['name'] = match[0].strip()
        if match[1].strip():
            author['email'] = match[1].strip()
        if match[2].strip():
            author['url'] = match[2].strip()
    return author


def extract_npm_package_author(package_json):
    """
    Extract package author from a ``package.json`` file content and
    return it in swh format.

    Args:
        package_json (dict): Dict holding the content of parsed
            ``package.json`` file

    Returns:
        dict: A dict with the following keys:
            * fullname
            * name
            * email

    """

    def _author_str(author_data):
        if type(author_data) is dict:
            author_str = ''
            if 'name' in author_data:
                author_str += author_data['name']
            if 'email' in author_data:
                author_str += ' <%s>' % author_data['email']
            return author_str
        elif type(author_data) is list:
            return _author_str(author_data[0]) if len(author_data) > 0 else ''
        else:
            return author_data

    author_data = {}
    for author_key in ('author', 'authors'):
        if author_key in package_json:
            author_str = _author_str(package_json[author_key])
            author_data = parse_npm_package_author(author_str)

    name = author_data.get('name')
    email = author_data.get('email')

    fullname = None

    if name and email:
        fullname = '%s <%s>' % (name, email)
    elif name:
        fullname = name

    if not fullname:
        return _EMPTY_AUTHOR

    if fullname:
        fullname = fullname.encode('utf-8')

    if name:
        name = name.encode('utf-8')

    if email:
        email = email.encode('utf-8')

    return {'fullname': fullname, 'name': name, 'email': email}


def _lstrip_bom(s, bom=BOM_UTF8):
    if s.startswith(bom):
        return s[len(bom):]
    else:
        return s


def load_json(json_bytes):
    """
    Try to load JSON from bytes and return a dictionary.

    First try to decode from utf-8. If the decoding failed,
    try to detect the encoding and decode again with replace
    error handling.

    If JSON is malformed, an empty dictionary will be returned.

    Args:
        json_bytes (bytes): binary content of a JSON file

    Returns:
        dict: JSON data loaded in a dictionary
    """
    json_data = {}
    try:
        json_str = _lstrip_bom(json_bytes).decode('utf-8')
    except UnicodeDecodeError:
        encoding = chardet.detect(json_bytes)['encoding']
        if encoding:
            json_str = json_bytes.decode(encoding, 'replace')
    try:
        json_data = json.loads(json_str)
    except json.decoder.JSONDecodeError:
        pass
    return json_data

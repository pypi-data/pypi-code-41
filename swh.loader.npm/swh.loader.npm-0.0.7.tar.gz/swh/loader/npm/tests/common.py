# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import os.path

from swh.loader.npm.utils import load_json

RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'resources')

empty_package = '22u-validators'
package = 'org'
package_non_utf8_encoding = '0b'


def package_url(package):
    return 'https://www.npmjs.com/package/%s' % package


def package_metadata_url(package):
    return 'https://replicate.npmjs.com/%s/' % package


def package_metadata_file(package, visit=''):
    json_filename = '%s_metadata' % package
    if visit:
        json_filename += '_visit%s' % visit
    json_filename += '.json'
    return json_filename


class _MockedFileStream():
    def __init__(self, file_data):
        self.file_data = file_data
        self.closed = False

    def read(self):
        self.closed = True
        return self.file_data


def init_test_data(m, package_metadata_json_file, package_metadata_url):

    package_metadata_filepath = os.path.join(RESOURCES_PATH,
                                             package_metadata_json_file)

    with open(package_metadata_filepath, 'rb') as json_file:
        json_file_bytes = json_file.read()
        package_metadata = load_json(json_file_bytes)

    m.register_uri('GET', package_metadata_url, json=package_metadata)

    for v, v_data in package_metadata['versions'].items():
        tarball_url = v_data['dist']['tarball']
        tarball_filename = tarball_url.split('/')[-1]
        tarball_filepath = os.path.join(RESOURCES_PATH, 'tarballs',
                                        tarball_filename)
        with open(tarball_filepath, mode='rb') as tarball_file:
            tarball_content = tarball_file.read()
            m.register_uri('GET', tarball_url,
                           body=_MockedFileStream(tarball_content))

    return package_metadata


def get_package_versions_data(package_metadata):
    versions_data = {}
    for v, v_data in package_metadata['versions'].items():
        shasum = v_data['dist']['shasum']
        versions_data[(v, shasum)] = {
            'name': package,
            'version': v,
            'sha1': shasum,
            'url': v_data['dist']['tarball'],
            'filename': v_data['dist']['tarball'].split('/')[-1],
            'date': package_metadata['time'][v]
        }
    return versions_data

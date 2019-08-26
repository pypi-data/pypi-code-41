# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import json
import os
import os.path
import tempfile
import unittest

import requests_mock

from swh.model import hashutil

from swh.loader.npm.client import NpmClient
from swh.loader.npm.utils import extract_npm_package_author

from .common import (
    RESOURCES_PATH, package, package_metadata_url,
    package_metadata_file, init_test_data,
    get_package_versions_data
)

PACKAGE_METADATA_JSON_FILENAME = package_metadata_file(package,
                                                       visit=1)
PACKAGE_METADATA_URL = package_metadata_url(package)


@requests_mock.Mocker()
class TestNpmClient(unittest.TestCase):

    def test_fetch_package_metadata(self, m):
        package_metadata = init_test_data(m, PACKAGE_METADATA_JSON_FILENAME,
                                          PACKAGE_METADATA_URL)
        with tempfile.TemporaryDirectory() as tempdir:
            npm_client = NpmClient(tempdir)
            npm_client.fetch_package_metadata(PACKAGE_METADATA_URL)
            self.assertEqual(npm_client.package_metadata, package_metadata)
            self.assertEqual(npm_client.package, package)

    def test_package_versions(self, m):
        package_metadata = init_test_data(m, PACKAGE_METADATA_JSON_FILENAME,
                                          PACKAGE_METADATA_URL)
        with tempfile.TemporaryDirectory() as tempdir:
            npm_client = NpmClient(tempdir)
            npm_client.fetch_package_metadata(PACKAGE_METADATA_URL)
            self.assertEqual(npm_client.latest_package_version(),
                             package_metadata['dist-tags']['latest'])

            self.assertEqual(npm_client.package_versions(),
                             get_package_versions_data(package_metadata))

    def test_prepare_package_versions(self, m):
        package_metadata = init_test_data(m, PACKAGE_METADATA_JSON_FILENAME,
                                          PACKAGE_METADATA_URL)
        package_versions_data = get_package_versions_data(package_metadata)
        with tempfile.TemporaryDirectory() as tempdir:
            npm_client = NpmClient(tempdir)
            npm_client.fetch_package_metadata(PACKAGE_METADATA_URL)
            versions_data = list(npm_client.prepare_package_versions())
            expected_versions_data = []
            for version, version_data in sorted(package_versions_data.items()):
                version = version[0]
                extracted_package_path = os.path.join(tempdir, package,
                                                      version, 'package')
                extracted_package_json_path = os.path.join(
                    extracted_package_path, 'package.json')
                self.assertTrue(os.path.isfile(extracted_package_json_path))
                with open(extracted_package_json_path) as package_json_file:
                    package_json = json.load(package_json_file)
                author = extract_npm_package_author(package_json)
                tarball_filepath = os.path.join(RESOURCES_PATH, 'tarballs',
                                                version_data['filename'])
                hash_names = hashutil.DEFAULT_ALGORITHMS - {'sha1_git'}
                hashes = hashutil.MultiHash.from_path(
                    tarball_filepath, hash_names=hash_names).hexdigest()
                version_data.update(hashes)
                expected_versions_data.append((package_json, author,
                                               version_data,
                                               extracted_package_path))
            self.assertEqual(versions_data, expected_versions_data)

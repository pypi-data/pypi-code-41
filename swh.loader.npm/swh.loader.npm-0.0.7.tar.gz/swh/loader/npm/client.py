# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import logging
import os

import requests

from swh.core import tarball
from swh.model import hashutil

from swh.loader.npm.utils import extract_npm_package_author, load_json


class NpmClient:
    """
    Helper class internally used by the npm loader to fetch
    metadata for a specific package hosted on the npm registry.

    Args:
        temp_dir (str): Path to the temporary disk location used
            to uncompress the package tarballs
    """
    def __init__(self, temp_dir, log=None):
        self.root_temp_dir = temp_dir
        self.session = requests.session()
        self.params = {
            'headers': {
                'User-Agent': 'Software Heritage npm loader'
            }
        }
        self.log = log or logging

    def fetch_package_metadata(self, package_metadata_url):
        """
        Fetch metadata for a given package and make it the focused one.
        This must be called prior any other operations performed
        by the other methods below.

        Args:
            package_metadata_url: the package metadata url provided
                by the npm loader
        """
        self.package_metadata_url = package_metadata_url
        self.package_metadata = self._request(self.package_metadata_url).json()
        self.package = self.package_metadata['name']
        self.temp_dir = os.path.join(self.root_temp_dir, self.package)

    def latest_package_version(self):
        """
        Return the last released version of the focused package.

        Returns:
            str: the last releases package version
        """
        latest = ''
        if 'latest' in self.package_metadata['dist-tags']:
            latest = self.package_metadata['dist-tags']['latest']
        return latest

    def package_versions(self, known_versions=None):
        """
        Return the available versions for the focused package.

        Args:
            known_versions (dict): may be provided by the loader, it enables
                to filter out versions already ingested in the archive.

        Returns:
            dict: A dict whose keys are Tuple[version, tarball_sha1] and
            values dicts with the following entries:

                    * **name**: the package name
                    * **version**: the package version
                    * **filename**: the package source tarball filename
                    * **sha1**: the package source tarball sha1 checksum
                    * **date**: the package release date
                    * **url**: the package source tarball download url
        """
        versions = {}
        if 'versions' in self.package_metadata:
            for version, data in self.package_metadata['versions'].items():
                sha1 = data['dist']['shasum']
                key = (version, sha1)
                if known_versions and key in known_versions:
                    continue
                tarball_url = data['dist']['tarball']
                filename = os.path.basename(tarball_url)
                date = self.package_metadata['time'][version]
                versions[key] = {
                    'name': self.package,
                    'version': version,
                    'filename': filename,
                    'sha1': sha1,
                    'date': date,
                    'url': tarball_url
                }
        return versions

    def prepare_package_versions(self, known_versions=None):
        """
        Instantiate a generator that will process a specific package released
        version at each iteration step. The following operations will be
        performed:

            1. Create a temporary directory to download and extract the
               release tarball
            2. Download the tarball
            3. Check downloaded tarball integrity
            4. Uncompress the tarball
            5. Parse ``package.json`` file associated to the package version
            6. Extract author from the parsed ``package.json`` file

        Args:
            known_versions (dict): may be provided by the loader, it enables
                to filter out versions already ingested in the archive.

        Yields:
            Tuple[dict, dict, dict, str]: tuples containing the following
            members:

                * a dict holding the parsed ``package.json`` file
                * a dict holding package author information
                * a dict holding package tarball information
                * a string holding the path of the uncompressed package to
                  load into the archive
        """
        new_versions = self.package_versions(known_versions)
        for version, package_source_data in sorted(new_versions.items()):
            # filter out version with missing tarball (cases exist),
            # package visit will be marked as partial at the end of
            # the loading process
            tarball_url = package_source_data['url']
            tarball_request = self._request(tarball_url,
                                            throw_error=False)
            if tarball_request.status_code == 404:
                self.log.debug('Tarball url %s returns a 404 error.',
                               tarball_url)
                self.log.debug(('Version %s of %s package will be missing and '
                                'the visit will be marked as partial.'),
                               version[0], self.package)
                continue
            version_data = self.package_metadata['versions'][version[0]]
            yield self._prepare_package_version(package_source_data,
                                                version_data)

    def _prepare_package_version(self, package_source_data, version_data):
        version = version_data['version']
        self.log.debug('Processing version %s for npm package %s',
                       version, self.package)

        # create temp dir to download and extract package tarball
        path = os.path.join(self.temp_dir, version)
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, package_source_data['filename'])

        # download tarball
        url = package_source_data['url']
        response = self._request(url)
        hash_names = hashutil.DEFAULT_ALGORITHMS - {'sha1_git'}
        h = hashutil.MultiHash(hash_names=hash_names)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=None):
                h.update(chunk)
                f.write(chunk)

        # check tarball integrity
        hashes = h.hexdigest()
        expected_digest = package_source_data['sha1']
        actual_digest = hashes['sha1']
        if actual_digest != expected_digest:
            raise ValueError(
                '%s %s: Checksum mismatched: %s != %s' % (
                    self.package, version, expected_digest, actual_digest))

        # uncompress tarball
        tarball_invalid = False
        try:
            tarball.uncompress(filepath, path)
        except Exception:
            tarball_invalid = True

        # remove tarball
        os.remove(filepath)

        if tarball_invalid:
            return (None, None, None, None)

        # do not archive useless tarball root directory
        package_path = os.path.join(path, 'package')
        # some old packages use a root directory with a different name
        if not os.path.exists(package_path):
            for _, dirnames, _ in os.walk(path):
                if dirnames:
                    package_path = os.path.join(path, dirnames[0])
                break

        self.log.debug('Package local path: %s', package_path)

        package_source_data.update(hashes)

        # parse package.json file to add its content to revision metadata
        package_json_path = os.path.join(package_path, 'package.json')
        package_json = {}
        with open(package_json_path, 'rb') as package_json_file:
            package_json_bytes = package_json_file.read()
            package_json = load_json(package_json_bytes)

        # extract author from package.json
        author = extract_npm_package_author(package_json)

        return (package_json, author, package_source_data, package_path)

    def _request(self, url, throw_error=True):
        response = self.session.get(url, **self.params, stream=True)
        if response.status_code != 200 and throw_error:
            raise ValueError("Fail to query '%s'. Reason: %s" % (
                url, response.status_code))
        return response

# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import shutil
from tempfile import mkdtemp
from urllib.parse import quote

from dateutil import parser as date_parser

from swh.loader.core.utils import clean_dangling_folders
from swh.loader.core.loader import BufferedLoader
from swh.model.from_disk import Directory
from swh.model.identifiers import (
    revision_identifier, snapshot_identifier,
    identifier_to_bytes, normalize_timestamp
)
from swh.storage.algos.snapshot import snapshot_get_all_branches

from swh.loader.npm.client import NpmClient


TEMPORARY_DIR_PREFIX_PATTERN = 'swh.loader.npm.'


class NpmLoader(BufferedLoader):
    """
    Loader for ingesting source packages from the npm registry
    into the Software Heritage archive.
    """

    CONFIG_BASE_FILENAME = 'loader/npm'
    ADDITIONAL_CONFIG = {
        'temp_directory': ('str', '/tmp/swh.loader.npm/'),
        'debug': ('bool', False)
    }

    visit_type = 'npm'

    def __init__(self):
        super().__init__(logging_class='swh.loader.npm.NpmLoader')
        temp_directory = self.config['temp_directory']
        os.makedirs(temp_directory, exist_ok=True)
        self.temp_directory = mkdtemp(suffix='-%s' % os.getpid(),
                                      prefix=TEMPORARY_DIR_PREFIX_PATTERN,
                                      dir=temp_directory)
        self.debug = self.config['debug']
        self.done = False
        self.npm_client = NpmClient(self.temp_directory, self.log)

    def pre_cleanup(self):
        """
        To prevent disk explosion if some other workers exploded
        in mid-air (OOM killed), we try and clean up dangling files.
        """
        if self.debug:
            self.log.warning('DEBUG: will not pre-clean up temp dir %s',
                             self.temp_directory)
            return
        clean_dangling_folders(self.config['temp_directory'],
                               pattern_check=TEMPORARY_DIR_PREFIX_PATTERN,
                               log=self.log)

    def cleanup(self):
        """
        Clean up temporary disk use after downloading and extracting
        npm source package tarballs.
        """
        if self.debug:
            self.log.warning('DEBUG: will not clean up temp dir %s',
                             self.temp_directory)
            return
        if os.path.exists(self.temp_directory):
            self.log.debug('Clean up %s', self.temp_directory)
            shutil.rmtree(self.temp_directory)

    def load(self, package_name, package_url=None,
             package_metadata_url=None):
        """
        Loader entrypoint to ingest source tarballs for a npm package.

        Args:
            package_name (str): the name of the npm package
            package_url (str): the url of the package description,
                if not provided the following one will be used:
                https://www.npmjs.com/package/<package_name>
            package_metadata_url (str): the url for the package JSON metadata,
                if not provided the following one will be used:
                https://replicate.npmjs.com/<package_name>/
        """
        if package_url is None:
            package_url = 'https://www.npmjs.com/package/%s' % package_name
        if package_metadata_url is None:
            package_metadata_url = 'https://replicate.npmjs.com/%s/' %\
                                    quote(package_name, safe='')
        return super().load(package_name, package_url, package_metadata_url)

    def prepare_origin_visit(self, package_name, package_url,
                             package_metadata_url):
        """
        Prepare npm package visit.

        Args:
            package_name (str): the name of the npm package
            package_url (str): the url of the package description
            package_metadata_url (str): the url for the package JSON metadata

        """
        # reset statuses
        self._load_status = 'uneventful'
        self._visit_status = 'full'
        self.done = False
        # fetch the npm package metadata from the registry
        self.npm_client.fetch_package_metadata(package_metadata_url)
        self.origin = {
            'url': package_url,
            'type': self.visit_type,
        }
        self.visit_date = None  # loader core will populate it

    def _known_versions(self, last_snapshot):
        """
        Retrieve the known release versions for the npm package
        (i.e. those already ingested into the archive).

        Args
            last_snapshot (dict): Last snapshot for the visit

        Returns:
            dict: Dict whose keys are Tuple[filename, sha1] and values
            are revision ids.

        """
        if not last_snapshot or 'branches' not in last_snapshot:
            return {}

        revs = [rev['target']
                for rev in last_snapshot['branches'].values()
                if rev and rev['target_type'] == 'revision']

        known_revisions = self.storage.revision_get(revs)
        ret = {}
        for revision in known_revisions:
            if not revision:
                continue
            if 'package_source' in revision['metadata']:
                package = revision['metadata']['package_source']
                ret[(package['version'], package['sha1'])] = revision['id']
        return ret

    def last_snapshot(self):
        """
        Retrieve the last snapshot of the npm package if any.
        """
        visit = self.storage.origin_visit_get_latest(
            self.origin['url'], require_snapshot=True)
        if visit:
            return snapshot_get_all_branches(self.storage, visit['snapshot'])

    def prepare(self, package_name, package_url, package_metadata_url):
        """
        Prepare effective loading of source tarballs for a npm
        package.

        Args:
            package_name (str): the name of the npm package
            package_url (str): the url of the package description
            package_metadata_url (str): the url for the package JSON metadata
        """
        self.package_name = package_name
        self.origin_url = package_url
        self.package_contents = []
        self.package_directories = []
        self.package_revisions = []
        self.package_load_status = 'uneventful'
        self.package_visit_status = 'full'

        last_snapshot = self.last_snapshot()
        self.known_versions = self._known_versions(last_snapshot)

        self.new_versions = \
            self.npm_client.prepare_package_versions(self.known_versions)

    def fetch_data(self):
        """
        Called once per package release version to process.

        This will for each call:
        - download a tarball associated to a package release version
        - uncompress it and compute the necessary information
        - compute the swh objects

        Returns:
            True as long as data to fetch exist

        """
        data = None
        if self.done:
            return False

        try:
            data = next(self.new_versions)
            self.package_load_status = 'eventful'
        except StopIteration:
            self.done = True
            return False

        package_metadata, author, package_source_data, dir_path = data

        # package release tarball was corrupted
        if package_metadata is None:
            return not self.done

        dir_path = dir_path.encode('utf-8')
        directory = Directory.from_disk(path=dir_path, data=True)
        objects = directory.collect()

        self.package_contents = objects['content'].values()
        self.package_directories = objects['directory'].values()

        date = date_parser.parse(package_source_data['date'])

        date = normalize_timestamp(int(date.timestamp()))

        message = package_source_data['version'].encode('ascii')

        revision = {
            'synthetic': True,
            'metadata': {
                'package_source': package_source_data,
                'package': package_metadata,
            },
            'author': author,
            'date': date,
            'committer': author,
            'committer_date': date,
            'message': message,
            'directory': directory.hash,
            'parents': [],
            'type': 'tar',
        }
        revision['id'] = identifier_to_bytes(revision_identifier(revision))

        self.package_revisions.append(revision)

        package_key = (package_source_data['version'],
                       package_source_data['sha1'])
        self.known_versions[package_key] = revision['id']

        self.log.debug('Removing unpacked package files at %s', dir_path)
        shutil.rmtree(dir_path)

        return not self.done

    def _target_from_version(self, version, sha1):
        """
        Return revision information if any for a given package version.
        """
        target = self.known_versions.get((version, sha1))
        return {
            'target': target,
            'target_type': 'revision',
        } if target else None

    def _generate_and_load_snapshot(self):
        """
        Generate snapshot for the npm package visit.
        """
        branches = {}
        latest_version = self.npm_client.latest_package_version()
        for version_data in self.npm_client.package_versions().values():
            version = version_data['version']
            sha1 = version_data['sha1']
            branch_name = ('releases/%s' % version).encode('ascii')
            target = self._target_from_version(version, sha1)
            branches[branch_name] = target
            if version == latest_version:
                branches[b'HEAD'] = {
                    'target_type': 'alias',
                    'target': branch_name,
                }
            if not target:
                self.package_visit_status = 'partial'
        snapshot = {
            'branches': branches,
        }
        snapshot['id'] = identifier_to_bytes(snapshot_identifier(snapshot))

        self.maybe_load_snapshot(snapshot)

    def store_data(self):
        """
        Send collected objects to storage.
        """
        self.maybe_load_contents(self.package_contents)
        self.maybe_load_directories(self.package_directories)
        self.maybe_load_revisions(self.package_revisions)

        if self.done:
            self._generate_and_load_snapshot()
            self.flush()

    def load_status(self):
        return {
            'status': self.package_load_status,
        }

    def visit_status(self):
        return self.package_visit_status


if __name__ == '__main__':
    import logging
    import sys
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) != 2:
        logging.error('Usage: %s <package-name>' % sys.argv[0])
        sys.exit(1)
    package_name = sys.argv[1]
    loader = NpmLoader()
    loader.load(package_name)

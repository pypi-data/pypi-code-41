# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import os
import unittest

import requests_mock

from unittest.mock import patch

from swh.core import tarball
from swh.loader.core.tests import BaseLoaderStorageTest
from swh.loader.npm.loader import NpmLoader
from swh.model.identifiers import snapshot_identifier

from .common import (
    empty_package, package, package_non_utf8_encoding,
    package_url, package_metadata_url, package_metadata_file,
    init_test_data,
)

_LOADER_TESTS_CONFIG = {
    'content_packet_size': 10000,
    'content_packet_size_bytes': 104857600,
    'content_size_limit': 104857600,
    'debug': False,
    'directory_packet_size': 25000,
    'occurrence_packet_size': 100000,
    'release_packet_size': 100000,
    'revision_packet_size': 100000,
    'send_contents': True,
    'send_directories': True,
    'send_releases': True,
    'send_revisions': True,
    'send_snapshot': True,
    'storage': {'args': {}, 'cls': 'memory'},
    'temp_directory': '/tmp/swh.loader.pypi/'
}

_expected_new_contents_first_visit = [
    '4ce3058e16ab3d7e077f65aabf855c34895bf17c',
    '858c3ceee84c8311adc808f8cdb30d233ddc9d18',
    '0fa33b4f5a4e0496da6843a38ff1af8b61541996',
    '85a410f8ef8eb8920f2c384a9555566ad4a2e21b',
    '9163ac8025923d5a45aaac482262893955c9b37b',
    '692cf623b8dd2c5df2c2998fd95ae4ec99882fb4',
    '18c03aac6d3e910efb20039c15d70ab5e0297101',
    '41265c42446aac17ca769e67d1704f99e5a1394d',
    '783ff33f5882813dca9239452c4a7cadd4dba778',
    'b029cfb85107aee4590c2434a3329bfcf36f8fa1',
    '112d1900b4c2e3e9351050d1b542c9744f9793f3',
    '5439bbc4bd9a996f1a38244e6892b71850bc98fd',
    'd83097a2f994b503185adf4e719d154123150159',
    'd0939b4898e83090ee55fd9d8a60e312cfadfbaf',
    'b3523a26f7147e4af40d9d462adaae6d49eda13e',
    'cd065fb435d6fb204a8871bcd623d0d0e673088c',
    '2854a40855ad839a54f4b08f5cff0cf52fca4399',
    'b8a53bbaac34ebb8c6169d11a4b9f13b05c583fe',
    '0f73d56e1cf480bded8a1ecf20ec6fc53c574713',
    '0d9882b2dfafdce31f4e77fe307d41a44a74cefe',
    '585fc5caab9ead178a327d3660d35851db713df1',
    'e8cd41a48d79101977e3036a87aeb1aac730686f',
    '5414efaef33cceb9f3c9eb5c4cc1682cd62d14f7',
    '9c3cc2763bf9e9e37067d3607302c4776502df98',
    '3649a68410e354c83cd4a38b66bd314de4c8f5c9',
    'e96ed0c091de1ebdf587104eaf63400d1974a1fe',
    '078ca03d2f99e4e6eab16f7b75fbb7afb699c86c',
    '38de737da99514de6559ff163c988198bc91367a',
]

_expected_new_contents_second_visit = [
    '135cb2000df4dfcfd8012d18ba23a54d6f89b105',
    '1e8e0943ee08958ab0a710dbba110f88068cab74',
    '25c8e3104daec559482ee1b480262be5da993e0e',
    '51245e983ebf91468fc59a072fcdddb837676abb',
    '55833e56224af0cf6fbbdca586c79d1e0e257b37',
    '785e0e16f2753b7683dd5f9e1bd1b98287334e6a',
    '876d655e927a95c7511853850c9c078be5f1a44b',
    'a2b331450408a22d3026c0444990b3235017c7e1',
    'a3f4f4d2055b21445defff5dada6cddb7c815f15',
    'b3aeed7cf5be703bd8a029928b431eecf5d205af',
    'b93d5e2006138f03e8ae84d0b72350fe6c37753a',
    'd196b2fa26032df86c8470e9f47a45cdeb5e23a2',
    'e3bae46f8f4f0347dab7ad567bf2f64bff3c1c53',
    'f2746efa0b38dcd3bbe7591cc075ee4a618c5943'
]

_expected_new_directories_first_visit = [
    '80579be563e2ef3e385226fe7a3f079b377f142c',
    '3b0ddc6a9e58b4b53c222da4e27b280b6cda591c',
    'bcad03ce58ac136f26f000990fc9064e559fe1c0',
    '5fc7e82a1bc72e074665c6078c6d3fad2f13d7ca',
    'e3cd26beba9b1e02f6762ef54bd9ac80cc5f25fd',
    '584b5b4b6cf7f038095e820b99386a9c232de931',
    '184c8d6d0d242f2b1792ef9d3bf396a5434b7f7a',
    'bb5f4ee143c970367eb409f2e4c1104898048b9d',
    '1b95491047add1103db0dfdfa84a9735dcb11e88',
    'a00c6de13471a2d66e64aca140ddb21ef5521e62',
    '5ce6c1cd5cda2d546db513aaad8c72a44c7771e2',
    'c337091e349b6ac10d38a49cdf8c2401ef9bb0f2',
    '202fafcd7c0f8230e89d5496ad7f44ab12b807bf',
    '775cc516543be86c15c1dc172f49c0d4e6e78235',
    'ff3d1ead85a14f891e8b3fa3a89de39db1b8de2e',
]

_expected_new_directories_second_visit = [
    '025bca14fcc9f84b7ebb09df4ec1b3fadd89a74c',
    '14f88da1a1efe2efe1bde2da9245ea1346ed49a0',
    '513965efeb9dc5832a8c69f354e57c0e1df4cb31',
    '5281878409fa2ab0d35feeef2fe6463346f4418d',
    '60b7c18bc5922a81060425edd7a623a4759ba657',
    '8c81ff424af1c26ff913e16d340f06ea7da0171c',
    '8c96171056490917a3b953c2a70cecace44f3606',
    '8faa8fbcbba90c36ab7dd076fd8fda5a9c405f8a',
    'b1224309f00536ea6f421af9f690bffab7bdb735',
    'c2f820f60db474714853c59765b0f914feb0fcfe',
    'e267845618e77ae0db8ca05428c0ee421df06a11',
    'e5a783a68869f7bc2fb9126b9100d98f18ea747c'
]

_expected_new_revisions_first_visit = {
    '969e0340155266e2a5b851e428e602152c08385f':
    '3b0ddc6a9e58b4b53c222da4e27b280b6cda591c',
    'c9b9ae8360ce8a1e22867226987f61163c12d4c4':
    '5fc7e82a1bc72e074665c6078c6d3fad2f13d7ca',
    '47831123f42cea24d6023e5570825cb62c3c1898':
    '5ce6c1cd5cda2d546db513aaad8c72a44c7771e2',
}

_expected_new_revisions_second_visit = {
    'a4ffa8770a901c895a67bec7a501036e83aae256':
    '8faa8fbcbba90c36ab7dd076fd8fda5a9c405f8a',
    'e6e41e3deb8df2b183f2d45e8f2e49a991c069a9':
    'b1224309f00536ea6f421af9f690bffab7bdb735',
    'ca12202b8a0eee7364204687649146e73e19ed32':
    '025bca14fcc9f84b7ebb09df4ec1b3fadd89a74c'
}

_expected_new_snapshot_first_visit = 'f2f59503de5a8aeabe7b68ce761d9e112713d996'

_expected_branches_first_visit = {
    'HEAD': {
        'target': 'releases/0.0.4',
        'target_type': 'alias'
    },
    'releases/0.0.2': {
        'target': '969e0340155266e2a5b851e428e602152c08385f',
        'target_type': 'revision'
    },
    'releases/0.0.3': {
        'target': 'c9b9ae8360ce8a1e22867226987f61163c12d4c4',
        'target_type': 'revision'
    },
    'releases/0.0.4': {
        'target': '47831123f42cea24d6023e5570825cb62c3c1898',
        'target_type': 'revision'
    }
}

_expected_new_snapshot_second_visit = '57957179a0ea016fcf9d02874b68547f2bd5698d' # noqa

_expected_branches_second_visit = {
    'HEAD': {
        'target': 'releases/0.2.0',
        'target_type': 'alias'
    },
    'releases/0.0.2': {
        'target': '969e0340155266e2a5b851e428e602152c08385f',
        'target_type': 'revision'
    },
    'releases/0.0.3': {
        'target': 'c9b9ae8360ce8a1e22867226987f61163c12d4c4',
        'target_type': 'revision'
    },
    'releases/0.0.4': {
        'target': '47831123f42cea24d6023e5570825cb62c3c1898',
        'target_type': 'revision'
    },
    'releases/0.0.5': {
        'target': 'a4ffa8770a901c895a67bec7a501036e83aae256',
        'target_type': 'revision'
    },
    'releases/0.1.0': {
        'target': 'e6e41e3deb8df2b183f2d45e8f2e49a991c069a9',
        'target_type': 'revision'
    },
    'releases/0.2.0': {
        'target': 'ca12202b8a0eee7364204687649146e73e19ed32',
        'target_type': 'revision'
    }
}


class NpmLoaderTest(NpmLoader):
    def parse_config_file(self, *args, **kwargs):
        return _LOADER_TESTS_CONFIG


@requests_mock.Mocker()
class TestNpmLoader(unittest.TestCase, BaseLoaderStorageTest):

    @classmethod
    def setUpClass(cls):
        cls.reset_loader()

    @classmethod
    def reset_loader(cls):
        cls.loader = NpmLoaderTest()
        cls.storage = cls.loader.storage

    def reset_loader_counters(self):
        counters_reset = dict.fromkeys(self.loader.counters.keys(), 0)
        self.loader.counters.update(counters_reset)

    def test_npm_loader_1_empty_package(self, m):

        init_test_data(m, package_metadata_file(empty_package),
                       package_metadata_url(empty_package))
        self.loader.load(empty_package, package_url(empty_package),
                         package_metadata_url(empty_package))

        self.assertCountContents(0)
        self.assertCountDirectories(0)
        self.assertCountRevisions(0)
        self.assertCountReleases(0)
        self.assertCountSnapshots(1)

        expected_branches = {}

        self.assertSnapshotEqual(
            snapshot_identifier({'branches': expected_branches}),
            expected_branches
        )

        self.assertEqual(self.loader.load_status(), {'status': 'uneventful'})
        self.assertEqual(self.loader.visit_status(), 'full')
        self.assertFalse(os.path.exists(self.loader.temp_directory))

    def test_npm_loader_2_first_visit(self, m):

        self.reset_loader()
        init_test_data(m, package_metadata_file(package, visit=1),
                       package_metadata_url(package))
        self.loader.load(package, package_url(package),
                         package_metadata_url(package))

        self.assertCountContents(len(_expected_new_contents_first_visit))
        self.assertCountDirectories(len(_expected_new_directories_first_visit))
        self.assertCountRevisions(3, '3 releases so 3 revisions should be created') # noqa
        self.assertCountReleases(0, 'No release is created by the npm loader')
        self.assertCountSnapshots(1, 'Only 1 snapshot targeting all revisions')

        self.assertContentsContain(_expected_new_contents_first_visit)
        self.assertDirectoriesContain(_expected_new_directories_first_visit)
        self.assertRevisionsContain(_expected_new_revisions_first_visit)
        self.assertSnapshotEqual(_expected_new_snapshot_first_visit,
                                 _expected_branches_first_visit)

        self.assertEqual(self.loader.counters['contents'],
                         len(_expected_new_contents_first_visit))
        self.assertEqual(self.loader.counters['directories'],
                         len(_expected_new_directories_first_visit))
        self.assertEqual(self.loader.counters['revisions'],
                         len(_expected_new_revisions_first_visit))
        self.assertEqual(self.loader.counters['releases'], 0)

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')
        self.assertFalse(os.path.exists(self.loader.temp_directory))

    def test_npm_loader_3_first_visit_again(self, m):

        self.reset_loader_counters()

        init_test_data(m, package_metadata_file(package, visit=1),
                       package_metadata_url(package))
        self.loader.load(package, package_url(package),
                         package_metadata_url(package))

        # previously loaded objects should still be here
        self.assertCountContents(len(_expected_new_contents_first_visit))
        self.assertCountDirectories(len(_expected_new_directories_first_visit))
        self.assertCountRevisions(len(_expected_new_revisions_first_visit))
        self.assertCountReleases(0)
        self.assertCountSnapshots(1)
        self.assertSnapshotEqual(_expected_new_snapshot_first_visit,
                                 _expected_branches_first_visit)

        # no objects should have been loaded in that visit
        counters_reset = dict.fromkeys(self.loader.counters.keys(), 0)
        self.assertEqual(self.loader.counters, counters_reset)

        self.assertEqual(self.loader.load_status(), {'status': 'uneventful'})
        self.assertEqual(self.loader.visit_status(), 'full')
        self.assertFalse(os.path.exists(self.loader.temp_directory))

    def test_npm_loader_4_second_visit(self, m):

        self.reset_loader_counters()

        init_test_data(m, package_metadata_file(package, visit=2),
                       package_metadata_url(package))
        self.loader.load(package, package_url(package),
                         package_metadata_url(package))

        expected_nb_contents = sum([len(_expected_new_contents_first_visit),
                                    len(_expected_new_contents_second_visit)])

        expected_nb_directories = sum([len(_expected_new_directories_first_visit), # noqa
                                       len(_expected_new_directories_second_visit)]) # noqa

        expected_nb_revisions = sum([len(_expected_new_revisions_first_visit),
                                     len(_expected_new_revisions_second_visit)]) # noqa

        self.assertCountContents(expected_nb_contents)
        self.assertCountDirectories(expected_nb_directories)
        self.assertCountRevisions(expected_nb_revisions)
        self.assertCountReleases(0)
        self.assertCountSnapshots(2)

        self.assertContentsContain(_expected_new_contents_first_visit)
        self.assertContentsContain(_expected_new_contents_second_visit)
        self.assertDirectoriesContain(_expected_new_directories_first_visit)
        self.assertDirectoriesContain(_expected_new_directories_second_visit)
        self.assertRevisionsContain(_expected_new_revisions_first_visit)
        self.assertRevisionsContain(_expected_new_revisions_second_visit)

        self.assertSnapshotEqual(_expected_new_snapshot_first_visit,
                                 _expected_branches_first_visit)
        self.assertSnapshotEqual(_expected_new_snapshot_second_visit,
                                 _expected_branches_second_visit)

        self.assertEqual(self.loader.counters['contents'],
                         len(_expected_new_contents_second_visit))
        self.assertEqual(self.loader.counters['directories'],
                         len(_expected_new_directories_second_visit))
        self.assertEqual(self.loader.counters['revisions'],
                         len(_expected_new_revisions_second_visit))
        self.assertEqual(self.loader.counters['releases'], 0)

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')
        self.assertFalse(os.path.exists(self.loader.temp_directory))

    def test_npm_loader_5_package_json_non_unicode_encoding(self, m):

        init_test_data(m, package_metadata_file(package_non_utf8_encoding),
                       package_metadata_url(package_non_utf8_encoding))
        self.loader.load(package_non_utf8_encoding,
                         package_url(package_non_utf8_encoding),
                         package_metadata_url(package_non_utf8_encoding))

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'full')
        self.assertFalse(os.path.exists(self.loader.temp_directory))

    @patch('swh.loader.npm.client.tarball')
    def test_npm_loader_6_invalid_tarball(self, m, mock_tarball):

        def _tarball_uncompress(filepath, path):
            if filepath.endswith('0.0.3.tgz'):
                raise Exception('Invalid tarball !')
            else:
                tarball.uncompress(filepath, path)

        mock_tarball.uncompress.side_effect = _tarball_uncompress

        self.reset_loader()
        init_test_data(m, package_metadata_file(package, visit=1),
                       package_metadata_url(package))
        self.loader.load(package, package_url(package),
                         package_metadata_url(package))

        snapshot = self.loader.last_snapshot()
        for branch, target in snapshot['branches'].items():
            if branch == b'releases/0.0.3':
                self.assertTrue(target is None)
            else:
                self.assertTrue(target is not None)

        self.assertEqual(self.loader.load_status(), {'status': 'eventful'})
        self.assertEqual(self.loader.visit_status(), 'partial')

# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>
#            Qixiang Wan <qwan@redhat.com>

import json
import mock
import os
import six
import shutil
import tempfile
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from argparse import Namespace
from ursa_major import MBS_BUILD_STATES
from ursa_major.handlers.update_tag import UpdateTagHandler


class TestUpdateTagHandler(unittest.TestCase):
    def setUp(self):
        config = mock.MagicMock()
        self.handler = UpdateTagHandler(config)

        self.handler.connect_koji = mock.MagicMock()
        self.handler._koji = mock.MagicMock()

        self.handler.connect_mbs = mock.MagicMock()
        self.handler._mbs = mock.MagicMock()

        self.tmpdir = tempfile.mkdtemp(suffix='_ursa_major_test')
        self.tag_config_file = os.path.join(self.tmpdir, 'default.json')
        tag_config = {
            'example-tag': {
                'owners': ['foo@example.com'],
                'modules': [
                    {'name': 'testmodule', 'stream': 'f30', 'priority': 10,
                     'requires': {'platform': 'f30'}},
                ]
            },
            'empty-tag': {
                'owners': ['foo@example.com'],
                'modules': []
            }
        }

        with open(self.tag_config_file, 'w') as f:
            json.dump(tag_config, f)

        self.set_args()

    def tearDown(self):
        try:
            shutil.rmtree(self.tmpdir)
        except:  # noqa
            pass

    def set_args(self, **kwargs):
        kwargs.setdefault('tag_config_file', self.tag_config_file)
        kwargs.setdefault('wait_regen_repo', False)
        kwargs.setdefault('dry_run', False)
        kwargs.setdefault('debug', False)
        kwargs.setdefault('tag', 'example-tag')
        args = Namespace()
        for k, v in kwargs.items():
            setattr(args, k, v)
        self.handler.set_args(args)

    def mock_get_tag(self, tag):
        taginfo = {
            "example-tag": {
                "name": "example-tag",
                "id": 123
            },
            "module-testmodule-f30-20180101-abc123": {
                "name": "module-testmodule-f30-20180101-abc123",
                "id": 10034
            },
            "module-testmodule-f30-20161212-000000": {
                "name": "module-testmodule-f30-20161212-000000",
                "id": 8080
            },
        }
        return taginfo.get(tag, {})

    def test_terminate_if_tag_not_in_config(self):
        self.set_args(tag='non-exist-tag')
        with six.assertRaisesRegex(self, RuntimeError, 'is not found in tag config file'):
            self.handler.run()

    def test_terminate_if_tag_not_in_koji(self):
        self.handler.koji.get_tag.return_value = None
        with six.assertRaisesRegex(self, RuntimeError, 'is not found in koji'):
            self.handler.run()

    @mock.patch('ursa_major.handlers.update_tag.log')
    def test_terminate_if_tag_has_no_module_in_config(self, log):
        self.set_args(tag='empty-tag')
        self.handler.run()
        log.warning.assert_any_call(
            "No module specified for tag '%s' in tag config file", "empty-tag")

    @mock.patch('ursa_major.handlers.update_tag.log')
    def test_skip_if_no_ready_build_found(self, log):
        self.handler.mbs.get_modules.return_value = []

        self.handler.run()
        log.warning.assert_has_calls([
            mock.call("There is no ready build found for %s, skipping", mock.ANY)
        ])

    @mock.patch('ursa_major.handlers.update_tag.log')
    def test_skip_if_tag_in_inheritance_with_same_priority(self, log):
        self.handler.mbs.get_modules.return_value = [
            {'koji_tag': 'module-testmodule-f30-20180101-abc123'}
        ]
        mock_inheritance = [
            {'name': 'module-testmodule-f30-20180101-abc123',
             'priority': 10}
        ]
        self.handler.koji.get_inheritance_data.return_value = mock_inheritance
        self.handler.run()
        log.info.assert_has_calls([
            mock.call("Tag '%s' is in inheritance data of %s with same priority, skipping",
                      "module-testmodule-f30-20180101-abc123", "example-tag")
        ])

    @mock.patch('ursa_major.handlers.update_tag.log')
    def test_tag_in_inheritance_with_different_priority(self, log):
        self.handler.mbs.get_modules.return_value = [
            {'koji_tag': 'module-testmodule-f30-20180101-abc123'}
        ]
        mock_inheritance = [
            {'name': 'module-testmodule-f30-20180101-abc123',
             'priority': 50}
        ]
        self.handler.koji.get_inheritance_data.return_value = mock_inheritance
        self.handler.run()
        self.handler.koji.set_inheritance_data.assert_has_calls([
            mock.call('example-tag',
                      [{'priority': 10, 'name': 'module-testmodule-f30-20180101-abc123'}])
        ])
        self.handler.koji.regen_repo.assert_has_calls([
            mock.call('example-tag', wait=False)
        ])

    @mock.patch('ursa_major.handlers.update_tag.log')
    def test_tag_not_in_inheritance_and_no_old_tag_found(self, log):
        self.handler.mbs.get_modules.return_value = [
            {'koji_tag': 'module-testmodule-f30-20180101-abc123'}
        ]

        self.handler.koji.get_tag.side_effect = self.mock_get_tag

        self.handler.koji.get_inheritance_data.return_value = []
        self.handler.run()
        inheritance_data = [
            {'intransitive': False,
             'name': 'module-testmodule-f30-20180101-abc123',
             'parent_id': 10034,
             'priority': 10,
             'maxdepth': None,
             'noconfig': False,
             'pkg_filter': '',
             'child_id': 123}
        ]
        self.handler.koji.set_inheritance_data.assert_has_calls([
            mock.call('example-tag', inheritance_data)
        ])
        self.handler.koji.regen_repo.assert_has_calls([
            mock.call('example-tag', wait=False)
        ])

    def test_tag_not_in_inheritance_and_old_tag_exist(self):
        mock_inheritance = [
            {'name': 'module-testmodule-f30-20161212-000000',
             'priority': 10}
        ]
        self.handler.koji.get_inheritance_data.return_value = mock_inheritance
        self.handler.koji.get_tag.side_effect = self.mock_get_tag

        def mock_get_modules(**kwargs):
            state = kwargs.get('state', None)
            if isinstance(state, list) and MBS_BUILD_STATES['garbage'] in state:
                # return all tags
                return [
                    {'koji_tag': 'module-testmodule-f30-20161212-000000'},
                    {'koji_tag': 'module-testmodule-f30-20180101-abc123'},
                ]
            else:
                # only return the latest one
                return [{'koji_tag': 'module-testmodule-f30-20180101-abc123'}]

        self.handler.mbs.get_modules.side_effect = mock_get_modules

        self.handler.run()

        call_args = self.handler.koji.set_inheritance_data.call_args.args
        self.assertEqual('example-tag', call_args[0])
        tag_to_remove = [t['name'] for t in call_args[1] if t.get('delete link', False) is True]
        tag_to_add = [t['name'] for t in call_args[1] if t.get('delete link', False) is False]
        self.assertTrue("module-testmodule-f30-20161212-000000" in tag_to_remove)
        self.assertTrue("module-testmodule-f30-20180101-abc123" in tag_to_add)
        self.handler.koji.regen_repo.assert_has_calls([
            mock.call('example-tag', wait=False)
        ])

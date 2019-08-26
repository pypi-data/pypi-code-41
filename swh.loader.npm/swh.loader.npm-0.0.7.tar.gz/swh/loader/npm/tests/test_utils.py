# Copyright (C) 2019  The Software Heritage developers
# See the AUTHORS file at the top-level directory of this distribution
# License: GNU General Public License version 3, or any later version
# See top-level LICENSE file for more information

import json
import os
import unittest

from swh.loader.npm.utils import (
    parse_npm_package_author, extract_npm_package_author
)
from swh.loader.npm.tests.common import (
    RESOURCES_PATH, package, package_metadata_file
)


class TestNpmClient(unittest.TestCase):

    def _parse_author_string_test(self, author_str, expected_result):
        self.assertEqual(
            parse_npm_package_author(author_str),
            expected_result
        )
        self.assertEqual(
            parse_npm_package_author(' %s' % author_str),
            expected_result
        )
        self.assertEqual(
            parse_npm_package_author('%s ' % author_str),
            expected_result
        )

    def test_parse_npm_package_author(self):

        self._parse_author_string_test(
            'John Doe',
            {
                'name': 'John Doe'
            }
        )

        self._parse_author_string_test(
            '<john.doe@foo.bar>',
            {
                'email': 'john.doe@foo.bar'
            }
        )

        self._parse_author_string_test(
            '(https://john.doe)',
            {
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            'John Doe <john.doe@foo.bar>',
            {
                'name': 'John Doe',
                'email': 'john.doe@foo.bar'
            }
        )

        self._parse_author_string_test(
            'John Doe<john.doe@foo.bar>',
            {
                'name': 'John Doe',
                'email': 'john.doe@foo.bar'
            }
        )

        self._parse_author_string_test(
            'John Doe (https://john.doe)',
            {
                'name': 'John Doe',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            'John Doe(https://john.doe)',
            {
                'name': 'John Doe',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            '<john.doe@foo.bar> (https://john.doe)',
            {
                'email': 'john.doe@foo.bar',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            '(https://john.doe) <john.doe@foo.bar>',
            {
                'email': 'john.doe@foo.bar',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            'John Doe <john.doe@foo.bar> (https://john.doe)',
            {
                'name': 'John Doe',
                'email': 'john.doe@foo.bar',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            'John Doe (https://john.doe) <john.doe@foo.bar>',
            {
                'name': 'John Doe',
                'email': 'john.doe@foo.bar',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            'John Doe<john.doe@foo.bar> (https://john.doe)',
            {
                'name': 'John Doe',
                'email': 'john.doe@foo.bar',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test(
            'John Doe<john.doe@foo.bar>(https://john.doe)',
            {
                'name': 'John Doe',
                'email': 'john.doe@foo.bar',
                'url': 'https://john.doe'
            }
        )

        self._parse_author_string_test('', {})
        self._parse_author_string_test('<>', {})
        self._parse_author_string_test(' <>', {})
        self._parse_author_string_test('<>()', {})
        self._parse_author_string_test('<> ()', {})
        self._parse_author_string_test('()', {})
        self._parse_author_string_test(' ()', {})

        self._parse_author_string_test(
            'John Doe <> ()',
            {
                'name': 'John Doe'
            }
        )

        self._parse_author_string_test(
            'John Doe <>',
            {
                'name': 'John Doe'
            }
        )

        self._parse_author_string_test(
            'John Doe ()',
            {
                'name': 'John Doe'
            }
        )

    def test_extract_npm_package_author(self):
        package_metadata_filepath = os.path.join(
            RESOURCES_PATH, package_metadata_file(package, visit=2))

        with open(package_metadata_filepath) as json_file:
            package_metadata = json.load(json_file)

        self.assertEqual(
            extract_npm_package_author(package_metadata['versions']['0.0.2']),
            {
                'fullname': b'mooz <stillpedant@gmail.com>',
                'name': b'mooz',
                'email': b'stillpedant@gmail.com'
            }
        )

        self.assertEqual(
            extract_npm_package_author(package_metadata['versions']['0.0.3']),
            {
                'fullname': b'Masafumi Oyamada <stillpedant@gmail.com>',
                'name': b'Masafumi Oyamada',
                'email': b'stillpedant@gmail.com'
            }
        )

        package_json = json.loads('''
        {
            "name": "highlightjs-line-numbers.js",
            "version": "2.7.0",
            "description": "Highlight.js line numbers plugin.",
            "main": "src/highlightjs-line-numbers.js",
            "dependencies": {},
            "devDependencies": {
                "gulp": "^4.0.0",
                "gulp-rename": "^1.4.0",
                "gulp-replace": "^0.6.1",
                "gulp-uglify": "^1.2.0"
            },
            "repository": {
                "type": "git",
                "url": "https://github.com/wcoder/highlightjs-line-numbers.js.git"
            },
            "author": "Yauheni Pakala <evgeniy.pakalo@gmail.com>",
            "license": "MIT",
            "bugs": {
                "url": "https://github.com/wcoder/highlightjs-line-numbers.js/issues"
            },
            "homepage": "http://wcoder.github.io/highlightjs-line-numbers.js/"
        }''') # noqa

        self.assertEqual(
            extract_npm_package_author(package_json),
            {
                'fullname': b'Yauheni Pakala <evgeniy.pakalo@gmail.com>',
                'name': b'Yauheni Pakala',
                'email': b'evgeniy.pakalo@gmail.com'
            }
        )

        package_json = json.loads('''
        {
            "name": "3-way-diff",
            "version": "0.0.1",
            "description": "3-way diffing of JavaScript objects",
            "main": "index.js",
            "authors": [
                {
                    "name": "Shawn Walsh",
                    "url": "https://github.com/shawnpwalsh"
                },
                {
                    "name": "Markham F Rollins IV",
                    "url": "https://github.com/mrollinsiv"
                }
            ],
            "keywords": [
                "3-way diff",
                "3 way diff",
                "three-way diff",
                "three way diff"
            ],
            "devDependencies": {
                "babel-core": "^6.20.0",
                "babel-preset-es2015": "^6.18.0",
                "mocha": "^3.0.2"
            },
            "dependencies": {
                "lodash": "^4.15.0"
            }
        }''')

        self.assertEqual(
            extract_npm_package_author(package_json),
            {
                'fullname': b'Shawn Walsh',
                'name': b'Shawn Walsh',
                'email': None
            }
        )

        package_json = json.loads('''
        {
            "name": "yfe-ynpm",
            "version": "1.0.0",
            "homepage": "http://gitlab.ywwl.com/yfe/yfe-ynpm",
            "repository": {
                "type": "git",
                "url": "git@gitlab.ywwl.com:yfe/yfe-ynpm.git"
            },
            "author": [
                "fengmk2 <fengmk2@gmail.com> (https://fengmk2.com)",
                "xufuzi <xufuzi@ywwl.com> (https://7993.org)"
            ],
            "license": "MIT"
        }''')

        self.assertEqual(
            extract_npm_package_author(package_json),
            {
                'fullname': b'fengmk2 <fengmk2@gmail.com>',
                'name': b'fengmk2',
                'email': b'fengmk2@gmail.com'
            }
        )

        package_json = json.loads('''
        {
            "name": "umi-plugin-whale",
            "version": "0.0.8",
            "description": "Internal contract component",
            "authors": {
                "name": "xiaohuoni",
                "email": "448627663@qq.com"
            },
            "repository": "alitajs/whale",
            "devDependencies": {
                "np": "^3.0.4",
                "umi-tools": "*"
            },
            "license": "MIT"
        }''')

        self.assertEqual(
            extract_npm_package_author(package_json),
            {
                'fullname': b'xiaohuoni <448627663@qq.com>',
                'name': b'xiaohuoni',
                'email': b'448627663@qq.com'
            }
        )

import json
import sys
from io import StringIO
from unittest.mock import patch

import pytest

from ocdsextensionregistry.cli.__main__ import main
from tests import read

args = ['ocdsextensionregistry', 'generate-data-file']


def test_command(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + ['location==v1.1.3'])
        main()

    assert actual.getvalue() == read('location-v1.1.3.json')


def test_command_latest_version_master(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + ['location==v1.1.3', 'location==master'])
        main()

    assert json.loads(actual.getvalue())['location']['latest_version'] == 'master'


def test_command_latest_version_dated(monkeypatch):
    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + ['location==v1.1.3', 'location==v1.1.1'])
        main()

    assert json.loads(actual.getvalue())['location']['latest_version'] == 'v1.1.3'


def test_command_missing_locale_dir(monkeypatch):
    with pytest.raises(SystemExit) as excinfo:
        with patch('sys.stdout', new_callable=StringIO) as out, patch('sys.stderr', new_callable=StringIO) as err:
            monkeypatch.setattr(sys, 'argv', args + ['--languages', 'es', 'location==v1.1.3'])
            main()

    assert out.getvalue() == ''
    assert '--locale-dir is required if --languages is set.' in err.getvalue()
    assert excinfo.value.code == 2


def test_command_directory(monkeypatch, tmpdir):
    versions_dir = tmpdir.mkdir('outputdir')
    version_dir = versions_dir.mkdir('location').mkdir('v1.1.3')

    version_dir.join('extension.json').write('{"name": "Location", "description": "…"}')
    version_dir.join('README.md').write('# Location')

    with patch('sys.stdout', new_callable=StringIO) as actual:
        monkeypatch.setattr(sys, 'argv', args + ['--versions-dir', str(versions_dir), 'location==v1.1.3'])
        main()

    assert json.loads(actual.getvalue()) == {
        'location': {
            'id': 'location',
            'category': 'item',
            'core': True,
            'name': {
                'en': 'Location',
            },
            'description': {
                'en': '…',
            },
            'latest_version': 'v1.1.3',
            'versions': {
                'v1.1.3': {
                    'id': 'location',
                    'date': '2018-02-01',
                    'version': 'v1.1.3',
                    'base_url': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.3/',  # noqa
                    'download_url': 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.3',  # noqa
                    'publisher': {
                        'name': 'open-contracting-extensions',
                        'url': 'https://github.com/open-contracting-extensions',
                    },
                    'metadata': {
                        'name': {
                            'en': 'Location',
                        },
                        'description': {
                            'en': '…',
                        },
                        'documentationUrl': {},
                        'compatibility': ['1.1'],
                    },
                    'schemas': {
                        'record-package-schema.json': {},
                        'release-package-schema.json': {},
                        'release-schema.json': {},
                    },
                    'codelists': {},
                    'readme': {
                        'en': '# Location\n',
                    },
                },
            },
        },
    }

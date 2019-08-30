import pytest

from ocdsextensionregistry import ExtensionVersion
from ocdsextensionregistry.exceptions import UnknownLatestVersion
from ocdsextensionregistry.util import get_latest_version


def test_get_latest_version_one():
    versions = [
        ExtensionVersion(arguments(**{'Version': '1'})),
    ]

    assert get_latest_version(versions).version == '1'


def test_get_latest_version_master():
    versions = [
        ExtensionVersion(arguments(**{'Version': '1'})),
        ExtensionVersion(arguments(**{'Date': None})),
        ExtensionVersion(arguments(**{'Date': '1000-01-01', 'Version': 'master'})),
    ]

    assert get_latest_version(versions).version == 'master'


def test_get_latest_version_dated():
    versions = [
        ExtensionVersion(arguments(**{'Version': '1'})),
        ExtensionVersion(arguments(**{'Date': None})),
        ExtensionVersion(arguments(**{'Date': '1000-01-01'})),
    ]

    assert get_latest_version(versions).version == '1'


def test_get_latest_version_dateless():
    versions = [
        ExtensionVersion(arguments(**{'Date': None})),
        ExtensionVersion(arguments(**{'Date': None, 'Version': '1'})),
    ]

    with pytest.raises(UnknownLatestVersion) as excinfo:
        get_latest_version(versions)

    assert str(excinfo.value) == ''


def arguments(**kwargs):
    data = {
        'Id': 'location',
        'Date': '2018-02-01',
        'Version': 'v1.1.3',
        'Base URL': 'https://raw.githubusercontent.com/open-contracting-extensions/ocds_location_extension/v1.1.3/',
        'Download URL': 'https://api.github.com/repos/open-contracting-extensions/ocds_location_extension/zipball/v1.1.3',  # noqa
    }

    data.update(kwargs)
    return data

import pytest
import mock
from utils import *


@pytest.mark.parametrize("mock_platform,extected_command", [
    ('win32', 'cmd /c start'),
    ('darwin', 'open'),
    ('cygwin', 'cygstart'),
    ('linux', 'xdg-open')
])
def test_start(mock_platform, extected_command):
    with mock.patch('sys.platform', mock_platform):
        url = 'https://github.com'
        with mock.patch('utils.call') as mock_call:
            mock_call.return_value = 0
            start(url)
            expected = '{} {}'.format(extected_command, url)
            mock_call.assert_called_once_with(expected)



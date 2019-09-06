import os
import six
import pytest
import mock
from crl.doc.robotws_util import create_dir, add_toc_tree  # pylint:disable=E0401


__copyright__ = 'Copyright (C), 2019 Nokia'
FILENAME = os.path.join("path", "to", "file", "file.txt")


@pytest.fixture
def mockopen():
    patch_str = "__builtin__.open" if six.PY2 else "builtins.open"
    with mock.patch(patch_str) as m:
        yield m


@pytest.fixture
def template():
    with mock.patch("crl.doc.robotws_util.Template") as m:
        yield m


@pytest.fixture
def oswalk():
    with mock.patch("crl.doc.robotws_util.os.walk") as m:
        yield m


@pytest.fixture
def mockOS():
    with mock.patch("crl.doc.robotws_util.os") as m:
        yield m


def test_check_if_directory_will_be_created_if_it_didnt_exist_before(mockOS):
    mockOS.path.exists.return_value = False
    mockOS.path.dirname.return_value = os.path.dirname(FILENAME)
    create_dir(FILENAME)
    mockOS.makedirs.assert_called_once_with(os.path.dirname(FILENAME))


def test_check_if_directory_wont_be_created_if_it_exists_before(mockOS):
    mockOS.path.exists.return_value = True
    mockOS.path.dirname.return_value = os.path.dirname(FILENAME)
    create_dir(FILENAME)
    with pytest.raises(AssertionError):
        mockOS.makedirs.assert_called_once_with(os.path.dirname(FILENAME))


def test_check_if_function_execute_correct_methods(template, mockopen, oswalk):
    template_render = mock.MagicMock()
    template_mock = mock.MagicMock(name="template")
    template_mock.render.return_value = template_render
    template.return_value = template_mock

    file_mock = mock.MagicMock(name="file")
    file_mock_enter = file_mock
    file_mock.__enter__.return_value = file_mock_enter
    mockopen.return_value = file_mock

    dirpath = os.path.join("path", "to", "directory")
    subdirectory_list = ('dir1', 'dir2', 'dir3')
    oswalk.return_value = ((dirpath, subdirectory_list, []),)
    add_toc_tree('root_dir', 'template_toc')
    for subdir in subdirectory_list:
        template_mock.render.assert_any_call(
            e=os.path.basename(os.path.join(dirpath, subdir)))
        file_mock_enter.write.assert_any_call(template_render)

import os
import errno
from collections import namedtuple
import pytest
import six
import mock
# pylint: disable=E0401
from jinja2 import TemplateError
from crl.doc.util import convert_xml_to_rst
from lxml.etree import LxmlError
# pylint: enable=E0401


__copyright__ = 'Copyright (C) 2019, Nokia'
FILENAME = os.path.join("path", "to", "file", "file.txt")
SRC_LIST = [os.path.join("path", "to", "src_file.xml"),
            os.path.join("path2", "t2", "src2_file.xml")]
DST_LIST = [os.path.join("path", "to", "dst_file.rst"),
            os.path.join("path2", "to2", "dst2_file.rst")]
TEMPLATE_FILE = os.path.join('template', 'dir', 'template.rst')
AUTHOR = 'Test AUTHOR'
MAINTAINER = 'Test MAINTAINER'
COMMITTER = "Test COMMITTER"
VERSION = "Test VERSION"


if six.PY2:
    from StringIO import StringIO  # pylint: disable=E0401
else:
    from io import StringIO


class Files(namedtuple('Files', ['src', 'template', 'dst'])):
    def create(self, **update):
        d = self._asdict()
        d.update(update)
        return Files(**d)


@pytest.fixture
def files(tmpdir):
    s = tmpdir.join('src')
    s.write('source content')
    t = tmpdir.join('template')
    t.write('template content')
    d = tmpdir.join('dst')
    return Files(src=str(s), template=str(t), dst=str(d))


@pytest.fixture
def mockOS():
    with mock.patch('crl.doc.util.os') as m:
        yield m


@pytest.fixture
def mock_create_dir():
    with mock.patch('crl.doc.util.create_dir') as m:
        yield m


@pytest.fixture
def objectify():
    with mock.patch('crl.doc.util.objectify') as m:
        yield m


@pytest.fixture
def template_cls():
    with mock.patch('crl.doc.util.Template') as m:
        yield m


@pytest.fixture
def mock_stdout():
    with mock.patch('sys.stdout', new_callable=StringIO) as m:
        yield m


@pytest.fixture(params=[OSError, LxmlError, TemplateError])
def exception(request):
    return request.param()


def test_check_if_directory_will_be_created_if_it_did_not_exist_before(mockOS,
                                                                       mock_create_dir):
    mockOS.path.isdir.return_value = False
    mockOS.path.dirname.return_value = os.path.dirname(FILENAME)
    mock_create_dir(FILENAME)
    with pytest.raises(AssertionError):
        mockOS.makedirs.assert_called_once_with(os.path.dirname(FILENAME))


def test_check_if_directory_wont_be_created_if_it_exists_before(mock_create_dir, mockOS):
    mockOS.path.exists.return_value = True
    mockOS.path.dirname.return_value = os.path.dirname(FILENAME)
    mock_create_dir(FILENAME)
    with pytest.raises(AssertionError):
        mockOS.makedirs.assert_called_once_with(os.path.dirname(FILENAME))


def test_template_was_rendered_correctly(template_cls, files, objectify):
    parse_mock = mock.MagicMock()

    def parse_side_effect(f):
        assert f.read() == 'source content'
        return parse_mock

    objectify.parse.side_effect = parse_side_effect
    root_mock = parse_mock.getroot.return_value
    template_mock = template_cls.return_value
    template_mock.render.return_value = "rendered content"
    convert_xml_to_rst(files.src, files.dst, files.template, AUTHOR, MAINTAINER, VERSION,
                       COMMITTER)
    parse_mock.getroot.assert_any_call()
    template_mock.render.assert_any_call(e=root_mock, author=AUTHOR,
                                         maintainer=MAINTAINER, version=VERSION,
                                         committer=COMMITTER)
    with open(files.dst, "rb") as f:
        assert f.read() == b"rendered content"


def test_template_fails_when_wrong_template_file(files):
    with pytest.raises(IOError):
        new_template = os.path.join(files.template, "wrongtemplate")
        convert_xml_to_rst(files.src, files.dst, new_template, AUTHOR, MAINTAINER,
                           VERSION, COMMITTER)


@pytest.mark.usefixtures('objectify', 'template_cls')
def test_template_fails_when_wrong_src_file(files, capsys):
    new_src = os.path.join(files.src, "wrongsrc")
    convert_xml_to_rst(new_src, files.dst, files.template, AUTHOR, MAINTAINER, VERSION,
                       COMMITTER)
    captured = capsys.readouterr()
    error_msg = "[Errno {}]".format(errno.ENOTDIR)
    assert error_msg in captured.out


@pytest.mark.usefixtures('objectify', 'template_cls')
def test_template_fails_when_wrong_dst_file(files, capsys):
    new_dst = os.path.join(files.dst, "wrongdst")
    convert_xml_to_rst(files.src, new_dst, files.template, AUTHOR, MAINTAINER, VERSION,
                       COMMITTER)
    captured = capsys.readouterr()
    error_msg = "[Errno {}]".format(errno.ENOENT)
    assert error_msg in captured.out

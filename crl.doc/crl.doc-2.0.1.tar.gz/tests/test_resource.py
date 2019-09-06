import os
import shutil
from filecmp import dircmp
import pytest
from crl.doc.resource import Resource


THISDIR = os.path.dirname(__file__)
RESOURCES = os.path.join(THISDIR, 'resources')
EXPECTED = os.path.join(THISDIR, 'expected')


@pytest.fixture(params=['onlysettings',
                        'variables',
                        'keywords',
                        'testcases',
                        'all'])
def resource(request):
    return request.param


def test_resource(tmpdir, resource):
    with tmpdir.as_cwd():
        tmpdir.mkdir('actual')
        shutil.copytree(RESOURCES, 'resources')
        r = Resource(src_path=os.path.join('resources', resource),
                     dst_path='actual')
        r.generate_rst()
        _assert_rst_files(resource)


def _assert_rst_files(resource):
    d = dircmp('actual', os.path.join(EXPECTED, resource))
    assert not d.diff_files
    assert not d.left_only
    assert not d.right_only

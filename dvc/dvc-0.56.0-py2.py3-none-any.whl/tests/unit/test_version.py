import mock
import subprocess


import dvc.version
from dvc.utils.compat import cast_bytes


def test_is_release():
    with mock.patch.object(dvc.version.subprocess, "check_output") as m:
        m.side_effect = subprocess.CalledProcessError(1, "cmd")
        ret = dvc.version._is_release(None, dvc.version._BASE_VERSION)
        assert ret is False

        m.side_effect = None
        m.return_value = cast_bytes(dvc.version._BASE_VERSION)
        ret = dvc.version._is_release(None, dvc.version._BASE_VERSION)
        assert ret

        m.return_value = cast_bytes("630d1741c2d5dd89a3176bd15b63121b905d35c9")
        ret = dvc.version._is_release(None, dvc.version._BASE_VERSION)
        assert ret is False

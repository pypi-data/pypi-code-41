import pytest

from void import Void


def test_metasingleton():
    assert Void() is Void


def test_newcall():
    try:
        Void()
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_getattr():
    try:
        Void.attr
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_setattr():
    try:
        Void.attr = 1
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_context():
    try:
        with Void as mgr:
            mgr.asd
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_getitem():
    try:
        Void['item'][1]
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_setitem():
    try:
        Void['item'] = 1
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_iter():
    try:
        for _ in Void:
            pass
    except Exception:
        pytest.fail("Unexpected Exception.")


def test_emptiness():
    assert list(Void) == []

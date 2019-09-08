# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the mod selection system
"""

import pytest
from portmod.repo.util import select_mod, LicenseDep
from portmod.repo.atom import Atom
from portmod.repo.loader import load_mod
from .env import setup_env, tear_down_env, select_profile


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    yield setup_env("test")
    tear_down_env()


@pytest.fixture()
def stable():
    """Sets up and cleans up the repo for tests"""
    select_profile("test")
    yield


@pytest.fixture()
def unstable():
    """Sets up and cleans up the repo for tests"""
    select_profile("test-unstable")
    yield


def test_select(stable):
    """Tests that we can select new mods over old ones"""
    mod1 = load_mod(Atom("test/test-1.0"))[0]
    mod2 = load_mod(Atom("test/test-2.0"))[0]
    assert select_mod([mod1, mod2]) == (mod2, None)


def test_select_stable(stable):
    """
    Tests that we don't select unstable mods if a stable version is available
    and we only accept stable keywords
    """
    mod1 = load_mod(Atom("test/test-1.0"))[0]
    mod2 = load_mod(Atom("test/test-2.0"))[0]
    mod3 = load_mod(Atom("test/test-2.0_rc1"))[0]
    assert select_mod([mod1, mod2, mod3]) == (mod2, None)


def test_select_unstable(unstable):
    """
    Tests that we select unstable mods if available
    and we accept unstable keywords
    """
    mod1 = load_mod(Atom("test/test-1.0"))[0]
    mod2 = load_mod(Atom("test/test-2.0"))[0]
    mod3 = load_mod(Atom("test/test-2.0_rc1"))[0]
    assert select_mod([mod1, mod2, mod3]) == (mod2, None)


def test_select_eula(stable):
    """
    Tests that trying to select a mod with an EULA creates a LicenseDep
    with the eula flag enabled
    """
    mod1 = load_mod(Atom("test/test-eula-1.0"))[0]
    mod, dep = select_mod([mod1])
    assert mod == mod1
    assert isinstance(dep, LicenseDep)
    assert dep.is_eula


def test_select_revision(stable):
    """
    Tests that we can successfully select the mod with the highest revision
    """
    mod1 = load_mod(Atom("test/test-1.0"))[0]
    mod2 = load_mod(Atom("test/test-1.0-r1"))[0]
    mod3 = load_mod(Atom("test/test-1.0-r2"))[0]
    assert select_mod([mod1, mod2, mod3]) == (mod3, None)

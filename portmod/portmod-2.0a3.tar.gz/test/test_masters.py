# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests file master detection
"""

import os
import pytest
from portmod.globals import env
from portmod.main import configure_mods
from portmod.masters import get_masters
from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup_repo():
    """sets up and tears down test environment"""
    yield setup_env("test")
    tear_down_env()


def test_masters_esp():
    """Tests that we detect esp masters properly"""

    configure_mods(["test/bloated-morrowind-1.0"], no_confirm=True)
    path = os.path.join(
        env.MOD_DIR, "test", "bloated-morrowind", "Bloated Morrowind.esp"
    )
    masters = get_masters(path)
    assert len(masters) == 1
    assert "Morrowind.esm" in masters

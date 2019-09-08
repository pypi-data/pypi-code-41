# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Portmod config tests
"""

import pytest
from portmod.globals import env
from portmod.config import get_config
from .env import setup_env, tear_down_env


@pytest.fixture(scope="module", autouse=True)
def setup():
    """
    Sets up and tears down the test environment
    """
    dictionary = setup_env("test")
    yield dictionary
    tear_down_env()


def test_profile_only_variables(setup):
    """
    Tests that sorting the config files works properly
    """
    get_config()
    with open(env.PORTMOD_CONFIG, "w") as configfile:
        print(
            f"""
USE_EXPAND = "FOO"
""",
            file=configfile,
        )
    get_config.cache_clear()
    with pytest.raises(UserWarning):
        get_config()

    with open(env.PORTMOD_CONFIG, "w") as configfile:
        print(
            f"""
ARCH = "BAR"
""",
            file=configfile,
        )

    get_config.cache_clear()
    with pytest.raises(UserWarning):
        get_config()

    with open(env.PORTMOD_CONFIG, "w") as configfile:
        print(
            f"""
TEST_PROFILE_ONLY = "BAR"
""",
            file=configfile,
        )

    get_config.cache_clear()
    with pytest.raises(UserWarning):
        get_config()

# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Functions to set up and tear down a testing environment
"""

import os
import shutil
import git
import portmod.repo.profiles
from portmod.globals import env
from portmod.config import get_config
from portmod.repos import Repo

TEST_REPO_DIR = os.path.join(os.path.dirname(__file__), "testrepo")
TEST_REPO = Repo("test", TEST_REPO_DIR, False, None, None, [], -1000)
_TMP_FUNC = None


def set_test_repo():
    """Replaces the repo list with one that just contains the test repo"""
    env.OLD_REPOS = env.REPOS
    env.REPOS = [TEST_REPO]


def setup_env(profile):
    """
    Sets up an entire testing environment
    All file writes will occur within a temporary directory as a result
    """
    cwd = os.getcwd()
    get_config.cache_clear()
    env.OLD = env.__dict__
    env.OLD_CWD = cwd
    env.TESTDIR = os.path.join(env.TMP_DIR, "test")
    env.PORTMOD_LOCAL_DIR = os.path.join(env.TESTDIR, "local")
    env.MOD_DIR = os.path.join(env.TESTDIR, "local", "mods")
    env.INSTALLED_DB = os.path.join(env.TESTDIR, "local", "db")
    env.PORTMOD_CONFIG_DIR = os.path.join(env.TESTDIR, "config")
    env.PORTMOD_CONFIG = os.path.join(env.TESTDIR, "config", "portmod.conf")
    os.makedirs(env.PORTMOD_CONFIG_DIR, exist_ok=True)
    select_profile(profile)
    gitrepo = git.Repo.init(env.INSTALLED_DB)
    gitrepo.config_writer().set_value("commit", "gpgsign", False).release()
    gitrepo.config_writer().set_value("user", "email", "pytest@example.com").release()
    gitrepo.config_writer().set_value("user", "name", "pytest").release()
    os.makedirs(env.TESTDIR, exist_ok=True)
    os.makedirs(os.path.join(env.TESTDIR, "local"), exist_ok=True)
    set_test_repo()
    return {
        "testdir": env.TESTDIR,
        "config": f"{env.TESTDIR}/config.cfg",
        "config_ini": f"{env.TESTDIR}/config.ini",
    }


def tear_down_env():
    """
    Reverts env to original state
    """
    os.chdir(env.OLD_CWD)
    env.__dict__ = env.OLD
    get_config.cache_clear()
    shutil.rmtree(env.TESTDIR)


def select_profile(profile):
    """Selects the given test repo profile"""
    global _TMP_FUNC
    if not _TMP_FUNC:
        _TMP_FUNC = portmod.repo.profiles.get_profile_path
    portmod.repo.profiles.get_profile_path = lambda: os.path.join(
        TEST_REPO_DIR, "profiles", profile
    )


def deselect_profile():
    """Reverts test profile selection"""
    global _TMP_FUNC
    if _TMP_FUNC:
        portmod.repo.profiles.get_profile_path = _TMP_FUNC

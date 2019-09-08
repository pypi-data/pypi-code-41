# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Tests the version comparison system
"""

from portmod.repo.util import get_max_version


def test_simple_version():
    """Tests extremely simple version comparison"""
    v_b = "2.0"
    v_a = "1.0"
    assert get_max_version([v_a, v_b]) == v_b


def test_suffix():
    """Tests that suffixed versions come before full versions"""
    assert (
        get_max_version(["2.0_alpha", "2.0_beta", "2.0_pre", "2.0_rc", "2.0"]) == "2.0"
    )


def test_suffix_p():
    """Tests that p suffixed versions come after full versions"""
    assert get_max_version(["2.0_p1", "2.0"]) == "2.0_p1"


def test_suffix_endings():
    """Tests that p suffixed versions with integer endings order correctly"""
    assert get_max_version(["2.0_p1", "2.0_p2"]) == "2.0_p2"
    assert get_max_version(["2.0_alpha1", "2.0_alpha2"]) == "2.0_alpha2"
    assert get_max_version(["2.0_alpha2", "2.0_beta1"]) == "2.0_beta1"
    assert get_max_version(["2.0_alpha", "2.0_alpha1"]) == "2.0_alpha1"


def test_letter():
    """
    Tests that letter versions come after non-letter versions, increase in order
    and take precedence over suffixes, but not numeric components
    """
    assert get_max_version(["2.0a", "2.0"]) == "2.0a"
    assert get_max_version(["2.0a", "2.0b"]) == "2.0b"
    assert get_max_version(["2.0a", "2.0b_alpha"]) == "2.0b_alpha"
    assert get_max_version(["2.1a", "2.0b"]) == "2.1a"


def test_revision():
    """
    Tests that revisions have the lowest precedence and increase in order
    """
    assert get_max_version(["2.0-r1", "2.0"]) == "2.0-r1"
    assert get_max_version(["2.0-r1", "2.0-r2"]) == "2.0-r2"
    assert get_max_version(["2.0a-r1", "2.0-r2"]) == "2.0a-r1"
    assert get_max_version(["2.0_beta-r1", "2.0_alpha-r2"]) == "2.0_beta-r1"

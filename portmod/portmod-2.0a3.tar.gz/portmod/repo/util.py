# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Various utility functions
"""

import re
from typing import Any, Iterable, Tuple
import hashlib
from collections import namedtuple
from functools import lru_cache
from portmod.repo.keywords import accepts, accepts_testing, get_keywords
from portmod.repo.metadata import has_eula, is_license_accepted
from ..config import get_config
from ..pybuild_interface import Pybuild

BUF_SIZE = 65536

VersionMatch = namedtuple(
    "VersionMatch", ["version", "numeric", "letter", "suffix", "revision"]
)
KeywordDep = namedtuple("KeywordDep", ["atom", "keyword"])
LicenseDep = namedtuple("LicenseDep", ["atom", "license", "is_eula"])


def select_mod(modlist: Iterable[Pybuild]) -> Tuple[Pybuild, Any]:
    """
    Chooses a mod version based on keywords and accepts it if the license is accepted
    """
    if not modlist:
        raise Exception("Cannot select mod from empty modlist")

    filtered = list(
        filter(lambda mod: accepts(get_keywords(mod.ATOM), mod.KEYWORDS), modlist)
    )

    keyword = None

    if filtered:
        mod = get_newest_mod(filtered)
    else:
        arch = get_config()["ARCH"]
        # No mods were accepted. Choose the best version and add the keyword
        # as a requirement for it to be installed
        unstable = list(
            filter(lambda mod: accepts_testing(arch, mod.KEYWORDS), modlist)
        )
        if unstable:
            mod = get_newest_mod(unstable)
            keyword = "~" + arch
        else:
            # There was no mod that would be accepted by enabling testing.
            # Try enabling unstable
            mod = get_newest_mod(modlist)
            keyword = "**"

    if not is_license_accepted(mod):
        return (mod, LicenseDep(mod.CMN, mod.LICENSE, has_eula(mod)))
    if keyword is not None:
        return (mod, KeywordDep("=" + mod.CM, keyword))

    return (mod, None)


def suffix_gt(a_suffix: str, b_suffix: str) -> bool:
    """Returns true iff a_suffix > b_suffix"""
    suffixes = ["alpha", "beta", "pre", "rc", "p"]
    return suffixes.index(a_suffix) > suffixes.index(b_suffix)


def get_max_version(versions: Iterable[str]) -> str:
    """
    Returns the largest version in the given list

    Version should be a valid version according to PMS section 3.2,
    optionally follwed by a revision
    """
    assert versions
    newest = None
    for version in versions:
        match = re.match(
            r"(?P<NUMERIC>[\d\.]+)"
            r"(?P<LETTER>[a-z])?_?"
            r"(?P<SUFFIX>([a-z]+\d*)*)"
            r"(-r(?P<REV>\d+))?",
            version,
        )
        assert match is not None
        v_match = VersionMatch(
            version=version,
            numeric=match.group("NUMERIC").split("."),
            letter=match.group("LETTER") or "",
            suffix=match.group("SUFFIX") or "",
            revision=int(match.group("REV") or "0"),
        )

        if not newest:
            newest = v_match
        else:
            done = False
            # Compare numeric components
            for index, val in enumerate(v_match.numeric):
                if index >= len(newest.numeric):
                    newest = v_match
                    done = True
                    break
                if int(val) > int(newest.numeric[index]):
                    newest = v_match
                    done = True
                    break
                elif int(val) < int(newest.numeric[index]):
                    done = True
                    break

            # Compare letter components
            if not done:
                if v_match.letter > newest.letter:
                    newest = v_match
                    continue
                elif v_match.letter < newest.letter:
                    continue

            # Compare suffixes
            if not done:
                if newest.suffix:
                    a_suffixes = newest.suffix.split("_")
                else:
                    a_suffixes = []
                if v_match.suffix:
                    b_suffixes = v_match.suffix.split("_")
                else:
                    b_suffixes = []
                for a_s, b_s in zip(a_suffixes, b_suffixes):
                    asm = re.match(r"(?P<S>[a-z]+)(?P<N>\d+)?", a_s)
                    bsm = re.match(r"(?P<S>[a-z]+)(?P<N>\d+)?", b_s)
                    assert asm
                    assert bsm
                    a_suffix = asm.group("S")
                    b_suffix = bsm.group("S")
                    a_suffix_num = int(asm.group("N") or "0")
                    b_suffix_num = int(bsm.group("N") or "0")
                    if a_suffix == b_suffix:
                        if b_suffix_num > a_suffix_num:
                            newest = v_match
                            done = True
                            break
                        elif a_suffix_num > b_suffix_num:
                            done = True
                            break
                    elif suffix_gt(b_suffix, a_suffix):
                        newest = v_match
                        done = True
                        break
                    else:
                        done = True
                        break
                # More suffixes implies an earlier version,
                # except when the suffix is _p
                if not done:
                    if len(a_suffixes) > len(b_suffixes):
                        if not a_suffixes[len(b_suffixes)].startswith("p"):
                            newest = v_match
                        done = True
                    elif len(a_suffixes) < len(b_suffixes):
                        if b_suffixes[len(a_suffixes)].startswith("p"):
                            newest = v_match
                        done = True

            # Compare revisions
            if not done:
                if v_match.revision > newest.revision:
                    newest = v_match
                    done = True
                elif v_match.revision < newest.revision:
                    done = True
    assert newest
    return newest.version


def get_newest_mod(modlist: Iterable[Pybuild]) -> Pybuild:
    """
    Returns the newest mod in the given list based on version
    If there is a tie, returns the earlier mod in the list
    """
    max_ver = get_max_version([mod.MVR for mod in modlist])
    for mod in modlist:
        if mod.MVR == max_ver:
            return mod
    raise Exception(
        f"Internal Error: get_max_version returned incorrect result {max_ver}"
    )


@lru_cache(maxsize=None)
def get_hash(filename: str, func=hashlib.sha512) -> str:
    """Hashes the given file"""
    hash_func = func()
    with open(filename, mode="rb") as archive:
        while True:
            data = archive.read(BUF_SIZE)
            if not data:
                break
            hash_func.update(data)
    return hash_func.hexdigest()

# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import AbstractSet, Iterable, List, Set, Tuple

import os
from collections import namedtuple
from portmod.repo.atom import Atom, QualifiedAtom
from portmod.globals import env
from .log import warn


Hash = namedtuple("Hash", ["alg", "value"])


class Source:
    """Class used for storing information about download files"""

    def __init__(self, url: str, name: str):
        self.url = url
        self.name = name
        self.hashes = []
        self.size = -1
        self.path = os.path.join(env.DOWNLOAD_DIR, name)
        basename, _ = os.path.splitext(name)
        # Hacky way to handle tar.etc having multiple extensions
        if basename.endswith("tar"):
            basename, _ = os.path.splitext(basename)

        self.basename = basename

    def manifest(self, size: int, hashes: Iterable[Hash]):
        """Updates source to include values in manifest"""
        self.size = size
        self.hashes = hashes

    def __repr__(self):
        return self.url


class InstallDir:
    def __init__(self, path, **kwargs):
        self.PATH = path
        self.REQUIRED_USE = kwargs.get("REQUIRED_USE", "")
        self.PATCHDIR = kwargs.get("PATCHDIR", ".")
        self.S = kwargs.get("S", None)
        source = kwargs.get("SOURCE", None)
        if self.S is None and source is not None:
            basename, _ = os.path.splitext(source)
            # Hacky way to handle tar.etc having multiple extensions
            if basename.endswith("tar"):
                basename, _ = os.path.splitext(basename)
            self.S = basename
            warn(
                "InstallDir.SOURCE is deprecated. "
                "Please consider changing this to InstallDir.S: "
                f"{source}"
            )

        self.WHITELIST = kwargs.get("WHITELIST", None)
        self.BLACKLIST = kwargs.get("BLACKLIST", None)
        self.RENAME = kwargs.get("RENAME", None)
        self.DATA_OVERRIDES = kwargs.get("DATA_OVERRIDES", "")
        for key in kwargs:
            if key not in {
                "REQUIRED_USE",
                "PATCHDIR",
                "SOURCE",
                "S",
                "WHITELIST",
                "BLACKLIST",
                "RENAME",
                "DATA_OVERRIDES",
            }:
                self.__dict__[key] = kwargs[key]

    def get_files(self):
        """Generator function yielding file subattributes of the installdir"""
        for key in self.__dict__:
            if isinstance(getattr(self, key), list):
                for item in getattr(self, key):
                    if isinstance(item, File):
                        yield item


class File:
    def __init__(self, name, **kwargs):
        self.NAME = name
        self.REQUIRED_USE = kwargs.get("REQUIRED_USE", "")
        self.OVERRIDES = kwargs.get("OVERRIDES", "") + " " + kwargs.get("MASTERS", "")


# Class used for typing pybuilds, allowing more flexibility with
# the implementations. Implementations of this class (e.g. Pybuild1)
# should derive it, but build file Mod classes should derive one of
# the implementations. This should be used as the type for any function that
# handles Pybuild objects.
#
# This provides a mechanism for modifying the Pybuild format, as we can
# make changes to this interface, and update the implementations to conform
# to it while keeping their file structure the same, performing conversions
# of the data inside the init function.
class Pybuild:
    """Interface describing the Pybuild Type"""

    ATOM: QualifiedAtom
    DISPLAY_ATOM: QualifiedAtom
    RDEPEND: str
    DEPEND: str
    SRC_URI: str
    MN: Atom
    MV: str
    MVR: str
    CATEGORY: str
    CMN: QualifiedAtom
    CM: QualifiedAtom
    REQUIRED_USE: str
    RESTRICT: str
    IUSE_EFFECTIVE: str
    IUSE: str
    TEXTURE_SIZES: str
    DESC: str
    NAME: str
    HOMEPAGE: str
    LICENSE: str
    KEYWORDS: str
    A: List[Source]
    AA: List[Source]
    USE: Set[str]
    REBUILD: str
    INSTALL_DIRS: List[InstallDir]

    def get_default_sources(self) -> List[Source]:
        """
        Returns a list of sources that are enabled
        with the current use configuration
        """

    def get_sources(
        self,
        uselist: AbstractSet[str] = set(),
        masklist: AbstractSet[str] = set(),
        matchnone=False,
        matchall=False,
    ) -> List[Source]:
        """
        Returns a list of sources that are enabled using the given configuration
        """

    def get_use(self) -> Tuple[Set[str], Set[str]]:
        """Returns the use flag configuration for the mod"""

    def get_restrict(self, *, matchall=False):
        """Returns parsed tokens in RESTRICT using current use flags"""

    def mod_nofetch(self):
        """
        Function to give user instructions on how to fetch a mod
        which cannot be fetched automatically
        """

    def valid_use(self, use: str) -> bool:
        """Returns whether or not the given flag is valid"""

    def get_dir_path(self, install_dir: InstallDir) -> str:
        """Returns the installed path of the given InstallDir"""

    def is_valid_flag(self, flag: str) -> bool:
        """Returns true if the given flag is a valid use flag for this mod"""


class InstalledPybuild(Pybuild):
    """Interface describing the type of installed Pybuilds"""

    INSTALLED_USE: Set[str]

    def get_installed_env(self):
        """Returns a dictionary containing installed object values"""

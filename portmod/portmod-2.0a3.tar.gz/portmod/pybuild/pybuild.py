# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import AbstractSet, List

import os
import shutil
import patoolib
import lzma
import json
import re
from git import Git
from pathlib import Path
from distutils.dir_util import copy_tree
from portmod.util import patch_dir
from portmod.globals import env
from portmod.repo.atom import Atom, InvalidAtom
from portmod.repo.use import get_use
from portmod.repo.usestr import use_reduce, check_required_use
from portmod.repo.manifest import get_manifest
from portmod.repo.metadata import (
    get_global_use,
    get_mod_metadata,
    license_exists,
    get_use_expand,
    check_use_expand_flag,
)
from ..repo.download import parse_arrow
from portmod.colour import colour
from colorama import Fore
from ..pybuild_interface import File, InstallDir, Pybuild, Source
from ..safemodules.io_guard import _check_call, IOType
from ..log import warn


def apply_patch(patch: str):
    """Applies git patch using Git apply"""
    print(f"Applying {patch}...")
    _check_call(patch, IOType.Read)
    _check_call(os.curdir, IOType.Write)
    for line in Git().apply([patch, "--numstat"]).split("\n"):
        file = line.split()[2]
        _check_call(file, IOType.Write)
        _check_call(file, IOType.Read)
    print(Git().apply([patch, "--stat", "--apply"]))


class Pybuild1(Pybuild):
    RDEPEND = ""
    DEPEND = ""
    DATA_OVERRIDES = ""
    IUSE = ""
    TIER = "a"
    KEYWORDS = ""
    LICENSE = ""
    NAME = ""
    DESC = ""
    HOMEPAGE = ""
    REBUILD = ""
    RESTRICT = ""
    TEXTURE_SIZES = ""
    REQUIRED_USE = ""
    SRC_URI = ""
    __ENV = None
    PATCHES = ""
    S = None
    INSTALL_DIRS: List[InstallDir] = []

    def __init__(self):
        filename = self.__class__.__pybuild__

        category = Path(filename).resolve().parent.parent.name
        self.ATOM = Atom(
            "{}/{}".format(category, os.path.basename(filename)[: -len(".pybuild")])
        )

        self.__REPO_PATH = Path(filename).resolve().parent.parent.parent
        repo_name_path = os.path.join(self.__REPO_PATH, "profiles", "repo_name")
        if os.path.exists(repo_name_path):
            with open(repo_name_path, "r") as repo_file:
                self.REPO = repo_file.readlines()[0].rstrip()
            self.DISPLAY_ATOM = "{}::{}".format(self.ATOM, self.REPO)

        self.M = Atom(self.ATOM.M)
        self.MN = Atom(self.ATOM.MN)
        self.MV = self.ATOM.MV
        self.MF = self.ATOM.MF
        self.MR = self.ATOM.MR or "r0"
        self.CATEGORY = self.ATOM.C
        self.R = self.ATOM.R
        self.CM = Atom(self.ATOM.CM)
        self.CMN = Atom(self.ATOM.CMN)
        self.MVR = self.ATOM.MVR

        self.IUSE_EFFECTIVE = set()

        self._manifest = get_manifest(filename)

        if self._manifest is None:
            raise Exception("Manifest not found!")
        if self._manifest.get(os.path.basename(filename)) is None:
            raise Exception("Pybuild not in manifest file!")
        if not self._manifest.get(os.path.basename(filename)).check(filename):
            raise Exception("Pybuild does not match entry in manifest file!")

        # Turn strings of space-separated atoms into lists
        if type(self.RDEPEND) is not str:
            raise TypeError("RDEPEND must be a string")

        if type(self.DEPEND) is not str:
            raise TypeError("DEPEND must be a string")

        if type(self.SRC_URI) is not str:
            raise TypeError("SRC_URI must be a string")

        if type(self.DATA_OVERRIDES) is not str:
            raise TypeError("DATA_OVERRIDES must be a string")

        if type(self.IUSE) is str:
            self.IUSE = set(self.IUSE.split())
            self.IUSE_EFFECTIVE |= set([use.lstrip("+") for use in self.IUSE])
        else:
            raise TypeError("IUSE must be a space-separated list of use flags")

        if type(self.KEYWORDS) is str:
            self.KEYWORDS = set(self.KEYWORDS.split())
        else:
            raise TypeError("KEYWORDS must be a space-separated list of keywords")

        if type(self.TIER) is int:
            self.TIER = str(self.TIER)
        elif type(self.TIER) is not str:
            raise TypeError("TIER must be a integer or string containing 0-9 or z")

        if type(self.LICENSE) is not str or not self.LICENSE:
            raise TypeError(
                "LICENSE must be a string containing a space separated list of licenses"
            )

        if type(self.RESTRICT) is not str:
            raise TypeError(
                "RESTRICT must be a string containing a space separated list"
            )

        if type(self.TEXTURE_SIZES) is str:
            texture_sizes = use_reduce(self.TEXTURE_SIZES, matchall=True)
            self.IUSE_EFFECTIVE |= set(
                ["texture_size_{}".format(size) for size in texture_sizes]
            )
        else:
            raise TypeError(
                "TEXTURE_SIZES must be a string containing a space separated list of "
                "texture sizes"
            )

        for use in get_use_expand(self.__REPO_PATH):
            if hasattr(self, use):
                self.IUSE_EFFECTIVE |= {
                    use.lower() + "_" + flag for flag in getattr(self, use, "").split()
                }

        all_sources = self.get_sources(matchall=True)

        for install in self.INSTALL_DIRS:
            if isinstance(install, InstallDir):
                if len(all_sources) > 0 and install.S is None:
                    if len(all_sources) == 1:
                        install.S = all_sources[0].basename
                    else:
                        raise Exception(
                            "InstallDir does not declare a source name but source "
                            "cannot be set automatically"
                        )
                elif not all_sources and install.S is None:
                    install.S = self.M
            else:
                raise TypeError(
                    "InstallDir {} should be of type InstallDir".format(install)
                )

    def get_use(self):
        return get_use(self)

    def get_manifest(self):
        return self._manifest

    def get_default_sources(self) -> List[Source]:
        (enabled, disabled) = get_use(self)
        return self.get_sources(enabled, disabled)

    def is_valid_flag(self, flag: str) -> bool:
        """Returns true if the given flag is a valid use flag for this mod"""
        return flag in self.IUSE_EFFECTIVE or hasattr(
            self, re.sub("_[^_]+$", "", flag.upper())
        )

    def get_sources(
        self,
        uselist: AbstractSet[str] = set(),
        masklist: AbstractSet[str] = set(),
        matchnone=False,
        matchall=False,
    ) -> List[Source]:
        sourcestr = self.SRC_URI
        sources = use_reduce(
            sourcestr,
            uselist,
            masklist,
            is_valid_flag=self.is_valid_flag,
            is_src_uri=True,
            flat=True,
            matchnone=matchnone,
            matchall=matchall,
        )
        grouped = parse_arrow(sources)

        manifest = self.get_manifest()

        for source in grouped:
            if manifest.get(source.name) is not None:
                m = manifest.get(source.name)
                source.manifest(m.SIZE, m.hashes)

        return grouped

    def get_restrict(self, *, matchall=False):
        """Returns parsed tokens in RESTRICT using current use flags"""
        if not matchall:
            (enabled, disabled) = self.get_use()
        else:
            (enabled, disabled) = ({}, {})

        return use_reduce(
            self.RESTRICT,
            enabled,
            disabled,
            is_valid_flag=self.is_valid_flag,
            flat=True,
            matchall=matchall,
        )

    def src_prepare(self):
        if self.PATCHES:
            enabled, disabled = self.get_use()
            for patch in use_reduce(self.PATCHES, enabled, disabled, flat=True):
                path = os.path.join(self.FILESDIR, patch)
                apply_patch(path)

    def valid_use(self, use: str):
        return use in self.IUSE_EFFECTIVE

    def src_install(self):
        for install_dir in self.INSTALL_DIRS:
            if check_required_use(
                install_dir.REQUIRED_USE, self.get_use()[0], self.valid_use
            ):
                print(
                    "Installing directory {} into {}".format(
                        install_dir.PATH, install_dir.PATCHDIR
                    )
                )
                source = os.path.normpath(
                    os.path.join(self.WORKDIR, install_dir.S, install_dir.PATH)
                )
                if install_dir.RENAME is None:
                    dest = os.path.normpath(os.path.join(self.D, install_dir.PATCHDIR))
                else:
                    dest = os.path.normpath(
                        os.path.join(
                            self.D,
                            os.path.join(install_dir.PATCHDIR, install_dir.RENAME),
                        )
                    )

                for file in install_dir.get_files():
                    # Remove files that aren't going to be used.
                    # We would like the user to enable them with use flags rather
                    # than manually
                    if not check_required_use(
                        file.REQUIRED_USE, self.get_use()[0], self.valid_use
                    ):
                        os.remove(os.path.join(source, file.NAME))

                if install_dir.WHITELIST is not None:
                    for file in install_dir.WHITELIST:
                        src_path = os.path.join(source, file)
                        dst_path = os.path.join(dest, file)
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        if os.path.isdir(src_path):
                            copy_tree(src_path, dst_path)
                        else:
                            shutil.copy(src_path, dst_path)
                elif install_dir.BLACKLIST is not None:
                    patch_dir(
                        source,
                        dest,
                        ignore=lambda directory, contents: [
                            os.path.basename(file)
                            for file in install_dir.BLACKLIST
                            if os.path.normpath(
                                os.path.join(source, os.path.dirname(file))
                            )
                            == os.path.normpath(directory)
                        ],
                    )
                else:
                    if os.path.islink(source):
                        linkto = os.readlink(source)
                        if os.path.exists(dest):
                            os.rmdir(dest)
                        os.symlink(linkto, dest, True)
                    else:
                        copy_tree(source, dest)
            else:
                print(
                    "Skipping directory {} due to unsatisfied use "
                    "requirements {}".format(install_dir.PATH, install_dir.REQUIRED_USE)
                )

    def mod_postinst(self):
        pass

    def mod_prerm(self):
        pass

    def validate(self):
        IUSE_STRIP = set([use.lstrip("+") for use in self.IUSE])
        errors = []

        try:
            use_reduce(self.RDEPEND, token_class=Atom, matchall=True)
            use_reduce(self.DEPEND, token_class=Atom, matchall=True)
            use_reduce(self.DATA_OVERRIDES, token_class=Atom, matchall=True)
            use_reduce(self.PATCHES, matchall=True)
        except InvalidAtom as e:
            errors.append("{}".format(e))
        except Exception as e:
            errors.append("{}".format(e))

        all_sources = self.get_sources([], [], matchall=True)

        for install in self.INSTALL_DIRS:
            if not isinstance(install, InstallDir):
                errors.append(
                    'InstallDir "{}" must have type InstallDir'.format(install.PATH)
                )
                continue
            for file in install.get_files():
                if not isinstance(file, File):
                    errors.append('File "{}" must have type File'.format(file))
                    continue

                try:
                    check_required_use(file.REQUIRED_USE, set(), self.valid_use)
                except Exception as e:
                    errors.append("Error processing file {}: {}".format(file.NAME, e))

            try:
                check_required_use(install.REQUIRED_USE, set(), self.valid_use)
            except Exception as e:
                errors.append("Error processing dir {}: {}".format(install.PATH, e))

            if len(all_sources) > 0 and not any(
                [install.S == source.basename for source in all_sources]
            ):
                warn(
                    'A source matching the basename "{}" '
                    "was not declared in SRC_URI".format(install.S)
                )
                print([source.basename for source in all_sources])

            if install.WHITELIST is not None and type(install.WHITELIST) is not list:
                errors.append("WHITELIST {} must be a list".format(install.WHITELIST))
            elif install.WHITELIST is not None:
                for string in install.WHITELIST:
                    if type(string) is not str:
                        errors.append(
                            "{} in InstallDir WHITELIST is not a string".format(string)
                        )

            if install.BLACKLIST is not None and type(install.BLACKLIST) is not list:
                errors.append("BLACKLIST {} must be a list".format(install.BLACKLIST))
            elif install.BLACKLIST is not None:
                for string in install.BLACKLIST:
                    if type(string) is not str:
                        errors.append(
                            "{} in InstallDir BLACKLIST is not a string".format(string)
                        )

            if install.WHITELIST is not None and install.BLACKLIST is not None:
                errors.append("WHITELIST and BLACKLIST are mutually exclusive")

        global_use = get_global_use(self.__REPO_PATH)
        metadata = get_mod_metadata(self)

        for use in IUSE_STRIP:
            if global_use.get(use) is None and (
                metadata is None or metadata.get("use", {}).get(use, None) is None
            ):
                errors.append(
                    'Use flag "{}" must be either a global use flag '
                    "or declared in metadata.yaml".format(use)
                )

        for value in self.get_restrict(matchall=True):
            if value not in {"fetch", "mirror"}:
                errors.append(f"Unsupported restrict flag {value}")

        if not self.NAME or "FILLME" in self.NAME or len(self.NAME) == 0:
            errors.append("Please fill in the NAME field")
        if not self.DESC or "FILLME" in self.DESC or len(self.DESC) == 0:
            errors.append("Please fill in the DESC field")
        if not self.HOMEPAGE or "FILLME" in self.HOMEPAGE or len(self.HOMEPAGE) == 0:
            errors.append("Please fill in the HOMEPAGE field")

        if not self.LICENSE:
            errors.append(
                "You must specify a LICENSE for the mod "
                "(i.e., the License the mod uses)"
            )
        else:
            for license in use_reduce(self.LICENSE, flat=True, matchall=True):
                if license != "||" and not license_exists(self.__REPO_PATH, license):
                    errors.append(
                        "LICENSE {} does not exit! Please make sure that it named "
                        "correctly, or if it is a new License that it is added to "
                        "the licenses directory of the repository".format(license)
                    )

        if not isinstance(self.PATCHES, str):
            errors.append("PATCHES must be a string")

        for use in get_use_expand(self.__REPO_PATH):
            for flag in getattr(self, use, "").split():
                if not check_use_expand_flag(self.__REPO_PATH, use, flag):
                    desc_path = os.path.join(
                        self.__REPO_PATH, "profiles", "desc", use.lower() + ".yaml"
                    )
                    errors.append(
                        f"flag {flag} for USE_EXPAND variable {use} "
                        f"does not exist in {desc_path}"
                    )

        if len(errors) > 0:
            raise Exception(
                "Pybuild {} contains the following errors:\n{}".format(
                    colour(Fore.GREEN, self.FILE), "\n".join(errors)
                )
            )

    def get_dir_path(self, install_dir):
        return os.path.join(env.MOD_DIR, self.CATEGORY, self.MN, install_dir.PATCHDIR)

    def get_file_path(self, install_dir, esp):
        return os.path.join(self.get_dir_path(install_dir), esp.NAME)

    def src_unpack(self):
        """Unpacks archives into the WORKDIR"""
        for archive in self.A:
            archive_name, ext = os.path.splitext(os.path.basename(archive.name))
            # Hacky way to handle tar.etc having multiple extensions
            if archive_name.endswith("tar"):
                archive_name, _ = os.path.splitext(archive_name)
            outdir = os.path.join(self.WORKDIR, archive_name)
            os.makedirs(outdir)
            patoolib.extract_archive(archive.path, outdir=outdir, interactive=False)

    def can_update_live(self):
        """
        Indicates whether or not a live mod can be updated.

        If the mod is a live mod and can be updated, return True
        Otherwise, return False
        """
        return False

    def get_installed_env(self):
        """Returns a dictionary containing installed object values"""
        if not self.INSTALLED:
            raise Exception("Trying to get environment for mod that is not installed")

        if self.__ENV is None:
            path = os.path.join(os.path.dirname(self.FILE), "environment.xz")
            if os.path.exists(path):
                environment = lzma.LZMAFile(path)
                self.__ENV = json.load(environment)
            else:
                self.__ENV = {}

        return self.__ENV

    def execute(self, command):
        """
        Allows execution of arbitrary commands at runtime.
        Command is sandboxed with filesystem and network access depending on
        the context in which it is called
        """
        raise Exception(f"execute was called from an invalid context in {self.M}")

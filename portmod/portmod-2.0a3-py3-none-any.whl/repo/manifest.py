# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Optional

import glob
from enum import Enum
import os
import hashlib
from portmod.repo.download import (
    download_source,
    get_hash,
    get_download,
    clobber_spaces,
)
from portmod.log import err
from .loader import load_file
from ..pybuild_interface import Hash


class ManifestMissing(Exception):
    """Inidcates a missing or invalid manifest entry"""


def grouper(n, iterable):
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * n
    return zip(*args)


class HashAlg:
    """
    Class for interacting with supported hash algorithms that can be used in manifests
    """

    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __repr__(self):
        return self.name


SHA512 = HashAlg("SHA512", hashlib.sha512)
HashAlgs = {"SHA512": SHA512}


class ManifestFile:
    def __init__(self, file):
        self.entries = {}
        self.FILE = file
        if os.path.exists(file):
            with open(file, "r") as manifest:
                for line in manifest.readlines():
                    words = line.split()
                    filetype = words[0]
                    name = words[1]
                    size = words[2]
                    hashes = []
                    if len(words) == 4:
                        hashes.append(Hash(SHA512, words[3]))
                    else:
                        for alg, value in grouper(2, words[3:]):
                            hashes.append(Hash(HashAlgs[alg], value))
                    self.entries[name] = Manifest(
                        name, FileType[filetype], size, hashes
                    )

    def add_entry(self, entry):
        if entry is None:
            raise Exception("Adding None to manifest")
        ours = self.entries.get(entry.NAME)
        if ours is None or not ours.to_string() == entry.to_string():
            self.entries[entry.NAME] = entry

    def write(self):
        with open(self.FILE, "w") as manifest:
            lines = [entry.to_string() for entry in self.entries.values()]
            lines.sort()
            for line in lines:
                print(line, file=manifest)

    def get(self, name: str) -> Optional[str]:
        return self.entries.get(name)


class FileType(Enum):
    PYBUILD = "PYBUILD"
    DIST = "DIST"
    AUX = "AUX"
    MISC = "MISC"


class Manifest:
    def __init__(self, name, filetype, size, hashes):
        self.NAME = name
        if type(filetype) is not FileType:
            raise Exception(
                "filetype {} of manifest entry must be a FileType".format(filetype)
            )
        self.FILE_TYPE = filetype
        self.hashes = hashes
        self.SIZE = int(size)

    def to_string(self):
        return "{} {} {} {}".format(
            self.FILE_TYPE.name,
            self.NAME,
            self.SIZE,
            " ".join([f"{h.alg} {h.value}" for h in self.hashes]),
        )

    def check(self, filename: str) -> bool:
        for h in self.hashes:
            return h.value == get_hash(filename, h.alg.func)

        return False


def create_manifest(mod):
    """
    Automatically downloads mod DIST files (if not already in cache)
    and creates a manifest file
    """
    clobber_spaces()
    pybuild_file = mod.FILE
    manifest = ManifestFile(manifest_path(pybuild_file))
    manifest.entries = {}

    directory = os.path.dirname(pybuild_file)

    for file in glob.glob(os.path.join(directory, "*.pybuild")):
        thismod = load_file(file)

        # Add ebuild to manifest
        manifest.add_entry(
            Manifest(
                os.path.basename(file),
                FileType.PYBUILD,
                os.path.getsize(file),
                [Hash(SHA512, get_hash(file))],
            )
        )

        sources = thismod.get_sources([], [], matchall=True)

        # Add sources to manifest
        for source in sources:
            filename = download_source(mod, source, False)
            if filename is None:
                err("Unable to get shasum for unavailable file " + source.name)
                continue

            shasum = get_hash(filename)
            hashes = [Hash(SHA512, shasum)]
            size = os.path.getsize(filename)

            manifest.add_entry(Manifest(source.name, FileType.DIST, size, hashes))

    metadata_file = os.path.join(os.path.dirname(pybuild_file), "metadata.yaml")
    # Add other files to manifest
    if os.path.exists(metadata_file):
        shasum = get_hash(metadata_file)
        hashes = [Hash(SHA512, shasum)]
        manifest.add_entry(
            Manifest(
                "metadata.yaml", FileType.MISC, os.path.getsize(metadata_file), hashes
            )
        )

    aux_dir = os.path.join(os.path.dirname(pybuild_file), "files")
    if os.path.exists(aux_dir):
        for file in os.listdir(aux_dir):
            path = os.path.join(aux_dir, file)
            shasum = get_hash(path)
            hashes = [Hash(SHA512, shasum)]
            manifest.add_entry(
                Manifest(file, FileType.AUX, os.path.getsize(path), hashes)
            )

    # Write changes to manifest
    manifest.write()


def verify_manifest(mod):
    """
    Verify that files match the manifest for a given mod.
    """
    clobber_spaces()
    pybuild_file = mod.FILE
    manifest = ManifestFile(manifest_path(pybuild_file))

    directory = os.path.dirname(pybuild_file)

    # Check that the files are in the manifest
    for file in glob.glob(os.path.join(directory, "*")):
        if os.path.basename(file) in {"files", "__pycache__", "Manifest"}:
            continue
        entry = manifest.get(os.path.basename(file))
        if not entry:
            raise ManifestMissing(
                f"{os.path.basename(file)} does not exist in the Manifest"
            )
        if not entry.check(file):
            raise ManifestMissing(
                f"Manifest entry for {os.path.basename(file)} is not valid"
            )

    for file in glob.glob(os.path.join(directory, "files", "*")):
        entry = manifest.get(os.path.basename(file))
        if not entry:
            raise ManifestMissing(
                f"{os.path.basename(file)} does not exist in the Manifest"
            )
        if not entry.check(file):
            raise ManifestMissing(
                f"Manifest entry for {os.path.basename(file)} is not valid"
            )

    # Check that the files in the manifest exist
    for entry in manifest.entries.values():
        if entry.FILE_TYPE == FileType.AUX:
            path = os.path.join(directory, "files", entry.NAME)
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"File {path} is in the manifest, but does not not exist"
                )
        elif entry.FILE_TYPE == FileType.MISC or entry.FILE_TYPE == FileType.PYBUILD:
            path = os.path.join(directory, entry.NAME)
            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"File {path} is in the manifest, but does not not exist"
                )


def manifest_path(file):
    return os.path.join(os.path.dirname(file), "Manifest")


# Loads the manifest for the given file, i.e. the Manifest file in the same directory
#    and turns it into a map of filenames to (shasum, size) pairs
def get_manifest(file):
    m_path = manifest_path(file)

    return ManifestFile(m_path)


def get_total_download_size(mods):
    download_bytes = 0
    for mod in mods:
        manifest_file = get_manifest(mod.FILE)
        for manifest in manifest_file.entries.values():
            if manifest.FILE_TYPE == FileType.DIST:
                download_bytes += manifest.SIZE

    return "{:.3f} MiB".format(download_bytes / 1024 / 1024)


def get_download_size(mods):
    clobber_spaces()
    download_bytes = 0
    for mod in mods:
        manifest_file = get_manifest(mod.FILE)
        sources = mod.get_default_sources()
        for manifest in manifest_file.entries.values():
            source = next(
                (source for source in sources if source.name == manifest.NAME), None
            )
            if (
                manifest.FILE_TYPE == FileType.DIST
                and source is not None
                and get_download(manifest.NAME, manifest.hashes) is None
            ):
                download_bytes += manifest.SIZE

    return "{:.3f} MiB".format(download_bytes / 1024 / 1024)

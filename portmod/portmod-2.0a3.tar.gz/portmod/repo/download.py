# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Iterable, List, Optional

import urllib
import urllib.request
import urllib.error
import urllib.parse
import os
import glob
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed

from portmod.repo.util import get_hash
from portmod.globals import env
from ..config import get_config
from ..pybuild_interface import Hash, Pybuild, Source


# Spaces are unweildy in download names. We enforce that source names in pybuilds
# do not contain spaces, however in the case of manual downloads, the files may
# contain spaces. Those spaces should be replaced with underscores in the pybuild,
# and we will ensure that any files placed in the download cache have their spaces
# replaced with underscores
def clobber_spaces():
    """Replaces spaces in cache file names with underscores"""
    filenames = glob.glob(os.path.join(env.DOWNLOAD_DIR, "* *"))
    for filename in filenames:
        os.rename(
            os.path.join(env.DOWNLOAD_DIR, filename),
            os.path.join(env.DOWNLOAD_DIR, filename.replace(" ", "_")),
        )


def parse_arrow(sourcelist: Iterable[str]) -> List[Source]:
    """
    Turns a list of urls using arrow notation into a list of
    Source objects
    """
    result = []
    arrow = False
    for value in sourcelist:
        if arrow:
            result[-1] = Source(result[-1].url, value)
            arrow = False
        elif value == "->":
            arrow = True
        else:
            url = urllib.parse.urlparse(value)
            result.append(Source(value, os.path.basename(url.path)))
    return result


def get_filename(basename: str) -> str:
    """
    Returns the location of the local cached version of the source file
    corresponding to the given name. The file may or may not exist.
    @return the cache location of the given source name
    """
    return os.path.join(env.DOWNLOAD_DIR, basename)


def download(url: str, destName: str):
    """
    Downloads the given url to the path specified by destName
    Raises exceptions as defined by urllib.request.urlretrieve
    """
    print("Fetching {}".format(url))
    bar = ProgressBar(
        widgets=[Percentage(), " ", Bar(), " ", ETA(), " ", FileTransferSpeed()],
        redirect_stdout=True,
    )

    def report(blocknum, blocksize, totalsize):
        if bar.max_value is None:
            if totalsize < 0:
                bar.start()
            else:
                bar.start(totalsize)
        bar.update(min(blocknum * blocksize, totalsize))

    os.makedirs(env.DOWNLOAD_DIR, exist_ok=True)
    urllib.request.urlretrieve(url, get_filename(destName), report)
    bar.finish()


def check_hash(filename: str, hashes: Iterable[Hash]) -> bool:
    """
    Returns true if and only if the sha512sum of the given file
    matches the given checksum
    """
    for h in hashes:
        return get_hash(filename, h.alg.func) == h.value
    return False


def get_download(name: str, hashes: Iterable[Hash]) -> Optional[str]:
    """
    Determines if the given file is in the cache.
    The file must match both name and checksum
    @return path to donloaded file
    """
    if os.path.exists(get_filename(name)) and check_hash(get_filename(name), hashes):
        return get_filename(name)
    return None


def is_downloaded(mod: Pybuild) -> bool:
    """
    Returns true if the mod's sources are all present in the cache
    """
    clobber_spaces()
    for source in get_sources(mod):
        cached = get_download(source.name, source.hashes)
        if cached is None:
            return False
    return True


def download_source(mod, source: Source, check: bool = True) -> str:
    """
    Downloads the given source file.
    @return the path to the downloaded source file
    """
    if check:
        cached = get_download(source.name, source.hashes)
    elif os.path.exists(get_filename(source.name)):
        cached = get_filename(source.name)
    else:
        cached = None
    fetch = "fetch" not in mod.get_restrict()
    mirror = "mirror" not in mod.get_restrict() and "fetch" not in mod.get_restrict()

    if cached:
        # Download is in cache. Nothing to do.
        return cached
    elif not fetch:
        # Mod cannot be fetched and is not already in cache. abort.
        raise Exception("Source {} not in cache and cannot be fetched".format(source))
    else:
        parsedurl = urllib.parse.urlparse(source.url)

        # Download archive
        filename = get_filename(source.name)

        if mirror:
            PORTMOD_MIRRORS = get_config()["PORTMOD_MIRRORS"].split()
            for mirror_url in PORTMOD_MIRRORS:
                url = urllib.parse.urljoin(mirror_url, source.name)
                try:
                    download(url, source.name)
                except urllib.error.HTTPError:
                    print("Unable to fetch {}.".format(url))
                    continue

                if check and not check_hash(filename, source.hashes):
                    raise Exception(
                        "Source file {} has invalid checksum!".format(source.name)
                    )

                return filename

        if parsedurl.scheme != "":
            download(source.url, source.name)
            if check and not check_hash(filename, source.hashes):
                raise Exception(
                    "Source file {} has invalid checksum!".format(source.name)
                )
            return filename

        raise Exception("Unable to download {}".format(source.url))


def get_sources(mod: Pybuild) -> List[Source]:
    """
    Returns list of mod sources in the mod's current configuration
    Excludes those that do not need to be downloaded due to use flag requirements
    """
    sources = mod.get_default_sources()
    return sources


def download_mod(mod: Pybuild, matchall=False) -> List[Source]:
    """
    Downloads missing sources for the given mod in its current USE configuration
    @return A list of paths of the sources for the mod
    """
    clobber_spaces()
    download_list = []
    if matchall:
        sources = mod.get_sources(matchall=True)
    else:
        sources = mod.get_default_sources()

    for source in sources:
        download_source(mod, source)

        download_list.append(source)

    return download_list

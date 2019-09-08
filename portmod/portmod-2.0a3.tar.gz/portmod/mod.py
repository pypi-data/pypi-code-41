# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Callable, Optional
import os
import shutil
import json
import lzma
import subprocess
import shlex
import sys
import git
from colorama import Fore
from portmod.globals import env
from portmod.repo.download import download_mod
from portmod.repo.loader import load_installed_mod
from portmod.colour import colour
from portmod.repo import Atom
from portmod.repo.config import remove_mod_config
from .log import warn


def get_execute(
    BUILD_DIR: str, network: Callable[[], bool]
) -> Callable[[str, bool], Optional[str]]:
    def execute(command: str, pipe_output: bool = False) -> Optional[str]:
        """Executes command"""
        nonlocal BUILD_DIR, network
        if sys.platform == "linux":
            pwd = os.getcwd()
            if network():
                dir_whitelist = [
                    "/bin",
                    "/lib",
                    "/lib32",
                    "/lib64",
                    "/opt",
                    "/usr",
                    "/var",
                ]
                bind_str = " ".join(
                    [
                        f"--ro-bind {path} {path}"
                        for path in dir_whitelist
                        if os.path.exists(path)
                    ]
                )
                sandbox_command = (
                    f"bwrap {bind_str} --dev /dev --proc /proc --unshare-all "
                    f"--share-net --bind {BUILD_DIR} {BUILD_DIR} --chdir {pwd}  "
                    f"--die-with-parent"
                )
            else:
                sandbox_command = (
                    f"bwrap --ro-bind / / --dev /dev --proc /proc --unshare-all "
                    f"--bind {BUILD_DIR} {BUILD_DIR} --chdir {pwd} --die-with-parent"
                )
        elif sys.platform == "win32":
            if network():
                sandbox_command = os.environ["SANDBOX_COMMAND_NETWORK"]
            else:
                sandbox_command = os.environ["SANDBOX_COMMAND"]
        elif sys.platform == "darwin":
            if network():
                sandbox_command = """sandbox-exec -p'
                    (version 1)
                    (deny default)
                    (allow network*)
                    (allow file-write* file-read*
                        (regex "^{BUILD_DIR}/")
                    )
                    (allow file-read-data file-read-metadata
                      (regex "^/dev/autofs.*")
                      (regex "^/usr/")
                      (regex "^/System/Library")
                      (regex "^/Applications/")
                      (regex "^/var")
                    )
                    (allow process-exec*)
                    '"""
            else:
                sandbox_command = """sandbox-exec -p '
                    (version 1)
                    (deny default)
                    (allow file-write* (regex "^{BUILD_DIR}/"))
                    (allow file-read*)
                    (allow process-exec*)
                    '"""
        else:
            raise Exception("Unsupported Platform")

        if pipe_output:
            with subprocess.Popen(
                shlex.split(sandbox_command + " " + command),
                bufsize=1,
                stdout=subprocess.PIPE,
            ) as proc:
                return proc.stdout.read()
        else:
            subprocess.check_call(
                shlex.split(sandbox_command + " " + command), bufsize=1
            )
            return None

    return execute


def remove_mod(mod, reinstall=False):
    """
    Removes the given mod
    @param reinstall if true, don't touch the installed DB since we'll
                      need it to finish the install
    """
    print("Removing " + colour(Fore.GREEN, mod.M))
    path = os.path.join(env.MOD_DIR, mod.CATEGORY, mod.MN)

    mod.USE = mod.INSTALLED_USE
    BUILD_DIR = os.path.join(env.TMP_DIR, mod.CATEGORY, mod.M)
    mod.T = os.path.join(BUILD_DIR, "temp")
    os.makedirs(mod.T, exist_ok=True)

    mod.ROOT = path
    os.chdir(mod.ROOT)
    mod.mod_prerm()
    mod.ROOT = None

    if os.path.exists(path):
        if os.path.islink(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    # Relies on the db to get old config entries,
    # so we must do this before we remove the db
    remove_mod_config(mod)

    db_path = os.path.join(env.INSTALLED_DB, mod.CATEGORY, mod.MN)
    if os.path.exists(db_path) and not reinstall:
        # Remove and stage changes
        gitrepo = git.Repo.init(env.INSTALLED_DB)
        gitrepo.git.rm(os.path.join(mod.CATEGORY, mod.MN), r=True, f=True)
        # Clean up unstaged files (e.g. pycache)
        shutil.rmtree(db_path, ignore_errors=True)

    print("Finished Removing " + colour(Fore.GREEN, mod.M))


def install_mod(mod):
    print("Starting installation of " + colour(Fore.GREEN, mod.M))
    sources = download_mod(mod)
    if sources is None:
        print("Unable to download mod. Aborting.")
        return False

    mod.A = sources
    mod.AA = mod.get_sources([], [], matchall=True)
    mod.USE = mod.get_use()[0]
    BUILD_DIR = os.path.join(env.TMP_DIR, mod.CATEGORY, mod.M)
    network = False

    mod.execute = get_execute(BUILD_DIR, lambda: network)
    # Ensure build directory is clean
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)

    mod.T = os.path.join(BUILD_DIR, "temp")
    mod.WORKDIR = os.path.join(BUILD_DIR, "work")
    mod.FILESDIR = os.path.join(os.path.dirname(mod.FILE), "files")
    os.makedirs(mod.WORKDIR, exist_ok=True)
    os.makedirs(mod.T, exist_ok=True)
    os.chdir(mod.WORKDIR)

    print("Unpacking Mod...")
    # Network access is allowed exclusively during src_unpack, and
    # adds additional filesystem restrictions to the sandbox
    network = True
    mod.src_unpack()
    network = False

    if not mod.S:
        tmp_source = next(iter(mod.get_default_sources()), None)
        if tmp_source:
            sourcedir, ext = os.path.splitext(tmp_source.name)
            # Hacky way to handle tar.etc having multiple extensions
            if sourcedir.endswith("tar"):
                sourcedir, _ = os.path.splitext(sourcedir)
            mod.S = os.path.join(mod.WORKDIR, sourcedir)

    if mod.S and os.path.exists(os.path.join(mod.WORKDIR, mod.S)):
        WORKDIR = os.path.join(mod.WORKDIR, mod.S)
    else:
        WORKDIR = mod.WORKDIR

    os.chdir(WORKDIR)
    mod.src_prepare()

    final_install_dir = os.path.join(env.MOD_DIR, mod.CATEGORY)
    os.makedirs(final_install_dir, exist_ok=True)
    final_install = os.path.join(final_install_dir, mod.MN)

    mod.D = os.path.join(BUILD_DIR, "image")
    os.makedirs(mod.D, exist_ok=True)
    os.chdir(WORKDIR)
    mod.src_install()

    os.chdir(env.TMP_DIR)

    # If a previous version of this mod was already installed,
    # remove it before doing the final copy
    old_mod = load_installed_mod(Atom(mod.CMN))
    db_path = os.path.join(env.INSTALLED_DB, mod.CATEGORY, mod.MN)
    if old_mod:
        remove_mod(old_mod, os.path.exists(db_path) and mod.INSTALLED)

    mod.mod_postinst()

    print("Installing into {}".format(final_install))

    if os.path.exists(final_install):
        warn("Installed directory already existed. Overwriting.")
        if os.path.islink(final_install):
            os.remove(final_install)
        else:
            shutil.rmtree(final_install)

    # base/morrowind links the D directory to the morrowind install.
    # Copy the link, not the morrowind install
    if os.path.islink(mod.D):
        linkto = os.readlink(mod.D)
        os.symlink(linkto, final_install)
    else:
        shutil.copytree(mod.D, final_install)

    # If installed database exists and there is no old mod, remove it
    if os.path.exists(db_path) and not old_mod:
        shutil.rmtree(db_path)

    # Update db entry for installed mod
    gitrepo = git.Repo.init(env.INSTALLED_DB)
    os.makedirs(db_path, exist_ok=True)

    # Copy pybuild to DB
    # unless source pybuild is in DB (i.e we're reinstalling)
    if not mod.FILE.startswith(db_path):
        shutil.copy(mod.FILE, db_path)
    gitrepo.git.add(os.path.join(mod.CATEGORY, mod.MN, os.path.basename(mod.FILE)))

    # Copy Manifest to DB
    if not mod.FILE.startswith(db_path):
        shutil.copy(os.path.join(os.path.dirname(mod.FILE), "Manifest"), db_path)
    gitrepo.git.add(os.path.join(mod.CATEGORY, mod.MN, "Manifest"))

    # Copy installed use configuration to DB
    with open(os.path.join(db_path, "USE"), "w") as use:
        print(" ".join(mod.get_use()[0]), file=use)
    gitrepo.git.add(os.path.join(mod.CATEGORY, mod.MN, "USE"))

    # Copy repo pybuild was from to DB
    with open(os.path.join(db_path, "REPO"), "w") as repo:
        print(mod.REPO, file=repo)
    gitrepo.git.add(os.path.join(mod.CATEGORY, mod.MN, "REPO"))

    # Write pybuild environment to DB
    with open(os.path.join(db_path, "environment.xz"), "wb") as environment:
        # Serialize as best we can. Sets become lists and unknown objects are
        # just stringified
        def dumper(obj):
            if isinstance(obj, set):
                return list(obj)
            return "{}".format(obj)

        # Keys are sorted to produce consistent results and
        # easy to read commits in the DB
        dictionary = mod.__class__.__dict__.copy()
        dictionary.update(mod.__dict__)
        jsonstr = json.dumps(dictionary, default=dumper, sort_keys=True)
        environment.write(lzma.compress(str.encode(jsonstr)))

    gitrepo.git.add(os.path.join(mod.CATEGORY, mod.MN, "environment.xz"))

    print("Installed " + colour(Fore.GREEN, mod.M))

    if not env.DEBUG:
        shutil.rmtree(BUILD_DIR)
        print(f"Cleaned up {BUILD_DIR}")
    return True

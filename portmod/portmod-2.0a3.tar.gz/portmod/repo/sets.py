# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Set
import os
from portmod.globals import env
from portmod.repo.atom import Atom
from .profiles import get_system


def get_set(mod_set: str, parent_dir: str = env.SET_DIR) -> Set[Atom]:
    if mod_set == "world" or mod_set == "rebuild":
        parent_dir = env.PORTMOD_LOCAL_DIR

    atoms = set()

    if mod_set == "world":
        atoms |= get_system()

    set_file = os.path.join(parent_dir, mod_set)
    if os.path.exists(set_file):
        with open(set_file, "r") as file:
            return atoms | set([Atom(s) for s in file.read().splitlines()])
    else:
        return atoms


def add_set(mod_set: str, atom: Atom, parent_dir: str = env.SET_DIR):
    if mod_set == "world" or mod_set == "rebuild":
        parent_dir = env.PORTMOD_LOCAL_DIR

    set_file = os.path.join(parent_dir, mod_set)
    os.makedirs(env.SET_DIR, exist_ok=True)
    if os.path.exists(set_file):
        with open(set_file, "r+") as file:
            for line in file:
                if atom in line:
                    break
            else:
                print(atom, file=file)
    else:
        with open(set_file, "a+") as file:
            print(atom, file=file)


def remove_set(mod_set: str, atom: Atom, parent_dir: str = env.SET_DIR):
    if mod_set == "world" or mod_set == "rebuild":
        parent_dir = env.PORTMOD_LOCAL_DIR

    set_file = os.path.join(parent_dir, mod_set)
    if os.path.exists(set_file):
        with open(set_file, "r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if atom not in line:
                    f.write(line)
            f.truncate()

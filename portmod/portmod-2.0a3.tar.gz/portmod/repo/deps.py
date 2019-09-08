# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Any, Dict, Iterable, List, Optional, Mapping, Set, Tuple

from functools import lru_cache
import sys
import shutil
import importlib
import io
from enum import Enum
from .loader import load_mod, load_all_installed, load_installed_mod
from .atom import Atom, atom_sat, newer_atom
from .sets import get_set
from .usestr import check_required_use, use_reduce
from .util import select_mod
from .manifest import get_download_size
from .profiles import get_system
from ..colour import green, bright, blue, yellow, red, lgreen
from ..tsort import CycleException, tsort
from ..pybuild_interface import Pybuild, InstalledPybuild
from ..config import get_config
from ..query import get_flag_string


class DepError(Exception):
    def __str__(self):
        return "Unable to satisfy " + " ".join(self.args)


class Trans(Enum):
    DELETE = "d"
    NEW = "N"
    UPDATE = "U"
    DOWNGRADE = "D"
    REINSTALL = "R"


class Transactions:
    mods: List[Tuple[Trans, Pybuild]]
    config: Set[Any]

    def __init__(self):
        self.mods = []
        self.config = set()

    def copy(self) -> "Transactions":
        new = Transactions()
        new.mods = self.mods.copy()
        new.config = self.config.copy()
        return new

    def extend(self, trans: "Transactions"):
        self.mods.extend(trans.mods)
        self.config |= trans.config


class UseDep:
    def __init__(self, atom: Atom, flag: str, oldvalue: Optional[str]):
        self.atom = atom
        self.flag = flag
        self.oldvalue = oldvalue


# Returns true if new mod object supercedes old mod object and false otherwise
# Raises exception if mods do not match
def newer_version(old, new):
    return newer_atom(old.ATOM, new.ATOM)


def print_transactions(
    mods, new_selected=[], new_usedep=[], verbose=False, out=sys.stdout, summarize=True
):
    download_size = get_download_size([mod for (_, mod) in mods])

    for (trans, mod) in mods:
        enabled_use, disabled_use = mod.get_use()
        for use in new_usedep:
            if atom_sat(mod.ATOM, use.atom):
                if use.flag.startswith("-"):
                    enabled_use.remove(use.flag.lstrip("-"))
                else:
                    enabled_use.add(use.flag)

        installed_mod = load_installed_mod(Atom(mod.CMN))
        if installed_mod is None:
            installed_use = None
        else:
            installed_use = installed_mod.INSTALLED_USE

        v = verbose or trans == Trans.NEW

        IUSE_STRIP = {flag.lstrip("+") for flag in mod.IUSE}

        oldver = ""
        texture_options = use_reduce(
            mod.TEXTURE_SIZES, enabled_use, disabled_use, flat=True, token_class=int
        )

        use_expand_strings = []
        for use in get_config().get("USE_EXPAND", []):
            if use in get_config().get("USE_EXPAND_HIDDEN", []):
                continue
            if hasattr(mod, use):
                enabled_expand = {
                    val
                    for val in get_config().get(use, "").split()
                    if val in getattr(mod, use).split()
                }
                disabled_expand = set(getattr(mod, use).split()) - enabled_expand
                if installed_use:
                    installed_expand = {
                        flag.lstrip(use.lower() + "_")
                        for flag in installed_use
                        if flag.startswith(use.lower() + "_")
                    }
                else:
                    installed_expand = None
                string = get_flag_string(
                    use, enabled_expand, disabled_expand, installed_expand, verbose=v
                )
                use_expand_strings.append(string)

        if mod.TEXTURE_SIZES is not None and len(texture_options) >= 2:
            texture_size = next(
                (
                    use.lstrip("texture_size_")
                    for use in enabled_use
                    if use.startswith("texture_size")
                ),
                None,
            )
            if texture_size is not None:
                texture_string = get_flag_string(
                    "TEXTURE_SIZE",
                    [texture_size],
                    map(str, sorted(set(texture_options) - {int(texture_size)})),
                )
            else:
                texture_string = ""
        else:
            texture_string = ""

        if trans == Trans.DELETE:
            trans_colour = red
        elif trans == Trans.NEW:
            trans_colour = lgreen
        elif trans == Trans.REINSTALL:
            trans_colour = yellow
        elif trans == Trans.DOWNGRADE or trans == Trans.UPDATE:
            trans_colour = blue
            installed_mod = load_installed_mod(Atom(mod.CMN))
            oldver = blue(" [" + installed_mod.MVR + "]")

        if verbose:
            modstring = mod.DISPLAY_ATOM
        else:
            modstring = mod.ATOM

        if is_selected(mod.ATOM) or mod in new_selected:
            modstring = bright(green(modstring))
        else:
            modstring = green(modstring)

        usestring = get_flag_string(
            "USE",
            enabled_use & IUSE_STRIP,
            IUSE_STRIP - enabled_use,
            installed_use,
            verbose=v,
        )

        print(
            "[{}] {}{}{}".format(
                bright(trans_colour(trans.value)),
                modstring,
                oldver,
                " "
                + " ".join(
                    list(filter(None, [usestring, texture_string] + use_expand_strings))
                ),
            ),
            file=out,
        )

    if summarize:
        print(
            "Total: {} mods ({} updates, {} new, {} reinstalls), "
            "Size of downloads: {}".format(
                len(mods),
                len(
                    [
                        trans
                        for (trans, _) in mods
                        if trans == Trans.UPDATE or trans == Trans.DOWNGRADE
                    ]
                ),
                len([trans for (trans, _) in mods if trans == Trans.NEW]),
                len([trans for (trans, _) in mods if trans == Trans.REINSTALL]),
                download_size,
            ),
            file=out,
        )


def get_all_deps(depstring: str) -> List[Atom]:
    dependencies = use_reduce(depstring, token_class=Atom, matchall=True, flat=True)

    # Note that any || operators will still be included. strip those out
    return list([dep for dep in dependencies if dep != "||"])


def use_changed(installed: InstalledPybuild) -> bool:
    """
    Checks whether or not the use flag configuration for the given mod
    has changed since it was installed.
    """
    (enabled, _) = installed.get_use()
    return enabled != installed.INSTALLED_USE


def sort_transactions(transactions: Transactions):
    """
    Create graph and do a topological sort to ensure that mods are installed/removed
    in the correct order given their dependencies
    """

    def get_dep_graph(keys):
        graph: Dict[Atom, Set[Atom]] = {}
        priorities = {}

        for (trans, mod) in transactions.mods:
            graph[mod.ATOM] = set()
            priorities[mod.ATOM] = mod.TIER

        for (trans, mod) in transactions.mods:
            depends = set()
            for dep in get_all_deps(" ".join([getattr(mod, key) for key in keys])):
                for (_, othermod) in transactions.mods:
                    if atom_sat(othermod.ATOM, dep):
                        depends.add(othermod.ATOM)
            if trans == Trans.DELETE:
                # When removing mods, remove them before their dependencies
                graph[mod.ATOM] |= depends
            else:
                # When adding or updating mods, mods, add or update their dependencies
                # before them
                for dep in depends:
                    graph[dep].add(mod.ATOM)
        return graph, priorities

    # Attempt to sort using both runtime and build dependencies. If this fails,
    # fall back to just build dependencies
    graph, priorities = get_dep_graph(["DEPEND", "RDEPEND"])
    try:
        mergeorder = tsort(graph, priorities)
    except CycleException:
        try:
            graph, priorities = get_dep_graph(["DEPEND"])
            mergeorder = tsort(graph, priorities)
        except CycleException:
            raise Exception(
                "Could not sort transactions; there is a cycle in dependency graph!"
            )

    new_trans = Transactions()
    for atom in mergeorder:
        for (trans, mod) in transactions.mods:
            if mod.ATOM == atom:
                new_trans.mods.append((trans, mod))
                break

    return new_trans


def is_selected(atom):
    selected = get_set("world")
    for selatom in selected:
        if atom_sat(atom, selatom):
            return True
    return False


def find_dependent(mods: Iterable[Pybuild]) -> Set[Pybuild]:
    """
    Takes a list of mods and Returns a set of installed mods
    that are dependent on the mods in the input list
    """
    installed = [mod for group in load_all_installed().values() for mod in group]
    dependent = set()

    for installed_mod in installed:
        for mod in mods:
            for atom in get_all_deps(installed_mod.RDEPEND) + get_all_deps(
                installed_mod.DEPEND
            ):
                if atom_sat(mod.ATOM, atom):
                    dependent.add(installed_mod)
                    break
    return dependent


def get_blocked(mod: Pybuild) -> Set[Atom]:
    (enabled, disabled) = mod.get_use()

    dependencies = use_reduce(
        mod.RDEPEND,
        enabled,
        disabled,
        is_valid_flag=mod.is_valid_flag,
        token_class=Atom,
        opconvert=True,
    ) + use_reduce(
        mod.DEPEND,
        enabled,
        disabled,
        is_valid_flag=mod.is_valid_flag,
        token_class=Atom,
        opconvert=True,
    )

    def parse_blocked(group):
        if type(group) is Atom:
            if group.BLOCK:
                return set([group])
            return set()

        # List of atoms, possibly prefixed by an operator
        elif type(group) is list and len(group) > 0:
            if group[0] == "||":  # Or Group. Try to match one mod in the group
                return parse_blocked(group[1:])
            else:
                results = set()
                for elem in group:
                    results |= parse_blocked(elem)
                return results
        else:
            return set()

    return parse_blocked(dependencies)


@lru_cache(maxsize=None)
def blocked() -> Mapping[str, List[Atom]]:
    """Creates list of mods blocked by already installed mods"""
    b: Dict[str, List[Atom]] = {}
    for mod in [mod for group in load_all_installed().values() for mod in group]:
        for block in get_blocked(mod):
            if block.MN in b:
                b[block.MN].append(block)
            else:
                b[block.MN] = [block]
    return b


def find_dependencies(transactions: Transactions) -> Transactions:
    """
    Takes a list of transactions and finds transactions that need to be done
    to to handle the dependencies of the input transactions.
    Returned list includes the original transactions
    """
    installed = load_all_installed()
    for (trans, mod) in transactions.mods:
        if installed.get(mod.MN) is not None:
            # If the mod was previously installed,
            # ensure that we use the new version instead
            installed[mod.MN] = [
                x for x in installed[mod.MN] if x.CATEGORY != mod.CATEGORY
            ]
            installed[mod.MN].append(mod)
        else:
            installed[mod.MN] = [mod]

    def is_satisfied(atom: Atom, transactions: Transactions) -> bool:
        """
        Checks if at least one of the atoms in the depends list
        is satisfied by an installed mod
        """
        if atom.C == "sys-bin":
            if not shutil.which(atom.MN):
                raise DepError(
                    f'Unable satisfy dependency on system executable "{atom.MN}"'
                )
            return True
        elif atom.C == "sys-python":
            try:
                importlib.import_module(atom.MN)
            except ImportError:
                raise DepError(
                    f'Unable satisfy dependency on python module "{atom.MN}"'
                )
            return True

        usedeps = atom.USE
        enabled_use = set([x for x in usedeps if not x.startswith("-")])
        disabled_use = set([x[1:] for x in usedeps if x.startswith("-")])
        MN = atom.MN
        if MN in installed:
            for i in installed.get(MN, []):
                if atom_sat(Atom(i.ATOM), atom):
                    (enabled, disabled) = i.get_use()
                    if enabled_use <= enabled and not any(
                        k in enabled for k in disabled_use
                    ):
                        return True

        # If a mod in the transaction list satisfies the atom, also return true
        for (trans, mod) in transactions.mods:
            if atom_sat(mod.ATOM, atom):
                (enabled, disabled) = mod.get_use()
                if enabled_use <= enabled and not any(
                    k in enabled for k in disabled_use
                ):
                    return True

        return False

    def get_trans(new_mod) -> Trans:
        """
        Determines the correct transaction for a new mod
        If not installed, Trans.NEW
        If already installed and version is the same, Trans.INSTALL
        If already installed with different version, Trans.UPDATE or Trans.DOWNGRADE
        """
        atom = Atom(new_mod.ATOM)
        if atom.MN in installed:
            for mod in installed[atom.MN]:
                otheratom = Atom(mod.ATOM)
                if otheratom.CMN == atom.CMN:
                    if not newer_atom(atom, otheratom) and not newer_atom(
                        otheratom, atom
                    ):
                        Trans.REINSTALL
                    elif newer_atom(atom, otheratom):
                        Trans.DOWNGRADE
                    else:
                        Trans.UPDATE
            return Trans.NEW
        else:
            return Trans.NEW

    def not_blocked(mod, changes) -> bool:
        """Returns true if the given mod is not blocked by any other installed mod"""
        global blocked
        if mod.MN in blocked():
            for atom in blocked()[mod.MN]:
                if atom_sat(mod.ATOM, Atom(atom)):
                    return False

        # TODO: it would be useful to cache this somehow
        for (trans, newmod) in changes.mods:
            for b in get_blocked(newmod):
                if atom_sat(mod.ATOM, b):
                    return False

        return True

    def satisfy_deps(group, transactions: Transactions) -> Transactions:
        """
        Finds a mod that satisfies one of the mods in the depends list
        The transactions list includes mods that have already been satisfied
          and should not be included in the result
        """
        new_trans = Transactions()
        if type(group) is Atom:  # Single atom
            # If it's a blocker, return true if not satisfied
            if group.BLOCK:
                if is_satisfied(group, transactions):
                    raise DepError(group)
                else:
                    return new_trans

            if not is_satisfied(group, transactions):
                # find mod that satisfies atom and add to mods
                pending_mods = list(
                    filter(lambda mod: not_blocked(mod, transactions), load_mod(group))
                )

                if len(pending_mods) > 0:
                    (new_mod, dep) = select_mod(pending_mods)
                    if dep is not None:
                        new_trans.config.add(dep)

                    if group.USE:
                        enabled, disabled = new_mod.get_use()
                        for use in group.USE:
                            if use.startswith("-"):
                                if use.lstrip("-") in enabled:
                                    new_trans.config.add(
                                        UseDep(
                                            Atom(new_mod.ATOM.CMN), use, use.lstrip("-")
                                        )
                                    )
                            elif use not in enabled:
                                if use in disabled:
                                    new_trans.config.add(
                                        UseDep(Atom(new_mod.ATOM.CMN), use, "-" + use)
                                    )
                                else:
                                    new_trans.config.add(
                                        UseDep(Atom(new_mod.ATOM.CMN), use, None)
                                    )

                    new_trans.mods.append((get_trans(new_mod), new_mod))
                    return new_trans

                raise DepError(group)
            return new_trans  # No dependencies to add if already satisfied

        elif type(group) is list:  # List of atoms, possibly prefixed by an operator
            if group[0] == "||":  # Or Group. Try to match one mod in the group
                for mod in group[1:]:
                    try:
                        return satisfy_deps(group[1:], transactions)
                    except DepError:
                        continue

                raise DepError(group)
            else:  # And Group. Try to match each mod in the group
                tmp = transactions.copy()
                for mod in group:
                    result = satisfy_deps([mod], tmp)
                    new_trans.extend(result)
                    tmp.extend(result)

                return new_trans
        raise Exception("Unknown token {} in dependencies!".format(group))

    def can_remove(atom: Atom):
        """
        Returns the mod object for this atom if it is installed and there
        are no installed mods that depend on this atom
        """
        mod = None
        for i in installed.get(atom.MN, []):
            if atom_sat(Atom(i.ATOM), atom):
                mod = i

        if mod is None:
            # Not actually installed
            return None

        for system_mod in get_system():
            # Mods in the system set cannot be removed
            if atom_sat(mod.ATOM, system_mod):
                return None

        dependent = [
            x
            for x in find_dependent([mod])
            if not any(
                [x == mod and trans == Trans.DELETE for trans, mod in new_mods.mods]
            )
        ]
        if len(dependent) == 0:
            return mod
        return None

    worklist = transactions.mods.copy()
    new_mods = transactions.copy()
    while len(worklist) > 0:
        (trans, mod) = worklist.pop()

        (enabled, disabled) = mod.get_use()

        dependencies = use_reduce(
            mod.RDEPEND,
            enabled,
            disabled,
            is_valid_flag=mod.is_valid_flag,
            token_class=Atom,
            opconvert=True,
        ) + use_reduce(
            mod.DEPEND,
            enabled,
            disabled,
            is_valid_flag=mod.is_valid_flag,
            token_class=Atom,
            opconvert=True,
        )

        for group in dependencies:
            if trans != Trans.DELETE:
                result = satisfy_deps(group, new_mods)
                worklist.extend(result.mods)
                new_mods.extend(result)

            else:
                # Check if there are any mods dependent on this dependency,
                #   and remove it if not
                to_remove = []

                if type(group) is Atom:  # Single atom
                    if is_selected(group) or group.BLOCK:
                        continue

                    m = can_remove(group)
                    if m is not None:
                        to_remove.append(m)
                elif type(group) is list:
                    if group[0] == "||":
                        for atom in group[1:]:
                            m = can_remove(atom)
                            if m is not None:
                                to_remove.append(m)
                    else:
                        for atom in group:
                            m = can_remove(atom)
                            if m is not None:
                                to_remove.append(m)

                worklist.extend([(Trans.DELETE, mod) for mod in to_remove])
                new_mods.mods.extend([(Trans.DELETE, mod) for mod in to_remove])

    # Ensure that required_use is satisfied
    for (trans, mod) in new_mods.mods:
        if trans != Trans.DELETE:
            (enabled, _) = mod.get_use()
            use_changes = list(filter(lambda x: isinstance(x, UseDep), new_mods.config))
            enabled |= {use.flag for use in use_changes if atom_sat(mod.ATOM, use.atom)}
            if not check_required_use(
                mod.REQUIRED_USE, enabled, lambda x: x in mod.IUSE_EFFECTIVE
            ):
                trans_str = io.StringIO()
                print_transactions(
                    [(trans, mod)],
                    out=trans_str,
                    summarize=False,
                    new_usedep=use_changes,
                )
                raise Exception(
                    f"REQUIRED_USE not satisfied for mod {mod.ATOM}: "
                    + human_readable_required_use(mod.REQUIRED_USE)
                    + f"\n{trans_str.getvalue()}"
                )

    return new_mods


def human_readable_required_use(required_use):
    return (
        required_use.replace("^^", "exactly-one-of")
        .replace("||", "any-of")
        .replace("??", "at-most-one-of")
    )

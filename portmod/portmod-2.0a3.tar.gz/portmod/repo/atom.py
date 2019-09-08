# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import AbstractSet, Optional, Set

import re

flag_re = r"[A-Za-z0-9][A-Za-z0-9+_-]*"
useflag_re = re.compile(r"^" + flag_re + r"$")
usedep_re = (
    r"(?P<prefix>[!-]?)(?P<flag>"
    + flag_re
    + r")(?P<default>(\(\+\)|\(\-\))?)(?P<suffix>[?=]?)"
)
_usedep_re = re.compile("^" + usedep_re + "$")

op_re = r"(?P<B>(!!))?(?P<OP>([<>]=?|[<>=]))?"
cat_re = r"((?P<C>[A-Za-z0-9\-]+)/)?"
ver_re = r"(\d+)((\.\d+)*)([a-z]?)((_(pre|p|beta|alpha|rc)\d*)*)"
rev_re = r"(-(?P<MR>r[0-9]+))?"
repo_re = r"(::(?P<R>.*))?"
_atom_re = re.compile(
    op_re
    + cat_re
    + r"(?P<M>(?P<MN>[A-Za-z0-9+_-]+?)(-(?P<MV>"
    + ver_re
    + r"))?)"
    + rev_re
    + repo_re
    + r"(\[(?P<USE>.*)\])?$"
)


class InvalidAtom(Exception):
    pass


class Atom(str):
    CM: Optional[str]
    CMN: Optional[str]
    USE: Set[str] = set()
    M: str
    MN: str
    MF: str
    MV: Optional[str]
    MR: Optional[str]
    C: Optional[str]
    R: Optional[str]
    OP: Optional[str]
    BLOCK: bool
    MVR: Optional[str]

    def __init__(self, atom: str):
        match = _atom_re.match(atom)
        if not match:
            raise InvalidAtom("Invalid atom %s. Cannot parse" % (atom))

        if match.group("M") and match.group("C"):
            self.CM = match.group("C") + "/" + match.group("M")
            self.CMN = match.group("C") + "/" + match.group("MN")
        else:
            self.CM = None
            self.CMN = None

        if match.group("USE"):
            self.USE = set(match.group("USE").split(","))
            for x in self.USE:
                m = _usedep_re.match(x)
                if not m:
                    raise InvalidAtom(
                        "Invalid use dependency {} in atom {}".format(atom, x)
                    )

        if match.group("MR"):
            self.MF = match.group("M") + "-" + match.group("MR")
        else:
            self.MF = match.group("M")

        self.M = match.group("M")
        self.MN = match.group("MN")
        self.MV = match.group("MV")
        self.MR = match.group("MR")
        self.C = match.group("C")
        self.R = match.group("R")
        self.OP = match.group("OP")
        self.BLOCK = match.group("B") is not None
        self.MVR = self.MV
        if self.MR:
            self.MVR += "-" + self.MR

        if self.OP is not None and self.MV is None:
            raise InvalidAtom(
                "Atom %s has a comparison operator but no version!" % (atom)
            )

    def evaluate_conditionals(self, use: AbstractSet[str]) -> "Atom":
        """
        Create an atom instance with any USE conditionals evaluated.
        @param use: The set of enabled USE flags
        @return: an atom instance with any USE conditionals evaluated
        """
        tokens = set()

        for x in self.USE:
            m = _usedep_re.match(x)

            if m is not None:
                operator = m.group("prefix") + m.group("suffix")
                flag = m.group("flag")
                default = m.group("default")
                if default is None:
                    default = ""

                if operator == "?":
                    if flag in use:
                        tokens.add(flag + default)
                elif operator == "=":
                    if flag in use:
                        tokens.add(flag + default)
                    else:
                        tokens.add("-" + flag + default)
                elif operator == "!=":
                    if flag in use:
                        tokens.add("-" + flag + default)
                    else:
                        tokens.add(flag + default)
                elif operator == "!?":
                    if flag not in use:
                        tokens.add("-" + flag + default)
                else:
                    tokens.add(x)
            else:
                raise Exception("Internal Error when processing atom conditionals")

        atom = Atom(self)
        atom.USE = tokens
        return atom


class QualifiedAtom(Atom):
    """Atoms that include categories"""

    CM: str
    CMN: str
    C: str


def newer_atom(old: Atom, new: Atom) -> bool:
    if old.CMN != new.CMN:
        raise Exception("Cannot compare versions of two different mods!")

    if isinstance(old.MV, str) and isinstance(new.MV, str):
        if old.MV == new.MV:  # If version numbers are the same
            if old.MR is not None and new.MR is not None:
                # If both mods have revisions, return true
                # if the new mod has the larger revision
                return int(old.MR[1:]) < int(new.MR[1:])
            elif new.MR is not None:
                # If only the new mod has a revision, it must be newer
                return True
            else:
                # If nether have revisions, then the versions are the same.
                # If the old one has a revision and the new one doesn't,
                # the old one is newer
                return False
        else:  # Versions are unequal
            oldver = old.MV.split(".")
            newver = new.MV.split(".")
            for i in range(0, min([len(oldver), len(newver)])):
                if newver[i] > oldver[i]:
                    return True
                elif newver[i] < oldver[i]:
                    return False
                # If they are the same, check the next part of the version

            # If we haven't already returned, then both strings match,
            # but one has more dots. Return the mod with the longer version
            return len(oldver) < len(newver)
    else:
        raise Exception("Unable to compare atoms that do not have versions!")


def atom_sat(specific: Atom, generic: Atom) -> bool:
    """
    Determines if a fully qualified atom (can only refer to a single package)
    satisfies a generic atom
    """

    if specific.MN != generic.MN:
        # Mods must have the same name
        return False

    if generic.C and (generic.C != specific.C):
        # If para defines category, it must match
        return False

    if generic.R and (generic.R != specific.R):
        # If para defines repo, it must match
        return False

    if not generic.OP:
        # Simple atom, either one version or all versions will satisfy

        # Check if version is correct
        if generic.MV and (specific.MV != generic.MV):
            return False

        # Check if revision is correct
        if generic.MR and (specific.MR != generic.MR):
            return False
    else:
        equal = specific.MV == generic.MV
        lessthan = newer_atom(specific, generic)
        greaterthan = newer_atom(generic, specific)

        if generic.OP == "=":
            return equal
        elif generic.OP == "<":
            return lessthan
        elif generic.OP == "<=":
            return equal or lessthan
        elif generic.OP == ">":
            return greaterthan
        elif generic.OP == ">=":
            return equal or greaterthan

    return True

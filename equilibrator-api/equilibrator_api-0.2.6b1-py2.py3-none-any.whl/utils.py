"""A utility module."""
from typing import List, Union

from equilibrator_api import Compound, ccache
from equilibrator_api.phased_reaction import PhasedReaction


def get_compound(compound_id: str) -> Union[Compound, None]:
    """Get a Compound using the DB namespace and its accession.

    :return: a Compound object or None
    """
    return ccache.get_compound(compound_id)


def get_compound_by_inchi(inchi: str) -> Union[Compound, None]:
    """Get a Compound using InChI.

    :return: a Compound object or None
    """
    return ccache.get_compound_by_inchi(inchi)


def search_compound_by_inchi_key(inchi_key: str) -> List[Compound]:
    """Get a Compound using InChI.

    :return: a Compound object or None
    """
    return ccache.search_compound_by_inchi_key(inchi_key)


def search_compound(query: str) -> Union[None, Compound]:
    """Try to find the compound that matches the name best.

    :param query: a compound name
    :return: a Compound object of the best match
    """
    hits = ccache.search(query)
    if not hits:
        return None
    else:
        return hits[0][0]


def parse_reaction_formula(formula: str) -> PhasedReaction:
    """Parse reaction text using exact match.

    :param formula: a string containing the reaction formula
    :return: a Reaction object
    """
    return PhasedReaction.parse_formula(ccache.get_compound, formula)


def search_reaction(formula: str) -> PhasedReaction:
    """Parse a reaction written using compound names and approximate matching.

    :param formula: a string containing the reaction formula
    :return: a Reaction object
    """
    return PhasedReaction.parse_formula(search_compound, formula)

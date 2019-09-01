from meta_sites import meta_sites

from .constants import ACTIVE, PLACEBO


class InvalidDrugAssignment(Exception):
    pass


def get_drug_assignment(row):
    """Returns drug_assignment as a word; 'single_dose' or 'control'.

    Converts a numeric drug_assignment or allocation
    to a word.
    """
    drug_assignment = row["drug_assignment"]
    if drug_assignment not in [ACTIVE, PLACEBO]:
        if int(row["drug_assignment"]) == 2:
            drug_assignment = ACTIVE
        elif int(row["drug_assignment"]) == 1:
            drug_assignment = PLACEBO
        else:
            raise InvalidDrugAssignment(
                f"Invalid drug assignment. "
                f'Got \'{row["drug_assignment"]}\'. Expected 1 or 2.'
            )
    return drug_assignment


def get_allocation(row, drug_assignment):
    """Returns an allocation as 1 or 2 for the given
    drug assignment or raises.
    """

    try:
        allocation = row["orig_allocation"]
    except KeyError:
        if drug_assignment == ACTIVE:
            allocation = "2"
        elif drug_assignment == PLACEBO:
            allocation = "1"
        else:
            raise InvalidDrugAssignment(
                f"Invalid drug_assignment. Got {drug_assignment}."
            )
    return allocation


def get_site_name(long_name, row=None):
    """Returns the site name given the "long" site name.
    """
    try:
        site_name = [site for site in meta_sites if site[2] == long_name][0][1]
    except IndexError as e:
        raise IndexError(f"{long_name} not found. Got {e}. See {row}")
    return site_name

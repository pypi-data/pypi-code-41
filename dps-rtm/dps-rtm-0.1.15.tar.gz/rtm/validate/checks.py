"""
Whereas the validation functions return results that will be outputted by the RTM Validator,
these "checks" functions perform smaller tasks, like checking individual cells.
"""

# --- Standard Library Imports ------------------------------------------------
from typing import Optional

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.main.context_managers as context


def cell_empty(value) -> bool:
    # If the cell contained True or False, then clearly it wasn't empty. Return False
    if isinstance(value, bool):
        return False
    if not value:
        return True
    return False


def get_expected_field_left(field):
    """Return the field object that *should* come before the argument field object."""
    initialized_fields = context.fields.get()
    index_prev_field = None
    for index, field_current in enumerate(initialized_fields):
        if field is field_current:
            index_prev_field = index - 1
            break
    if index_prev_field is None:
        raise ValueError
    elif index_prev_field == -1:
        return None
    else:
        return initialized_fields[index_prev_field]


def dict_contains_only_acceptable_entries(dictionary, acceptible_entries):
    if len(dictionary) == 0:
        return True
    for value in dictionary.values():
        if value not in acceptible_entries:
            return False
    return True


allowed_cascade_levels = {  # keys: level, values: position
        'PROCEDURE STEP': [0],
        'VOC USER NEED': [1],
        'BUSINESS NEED': [1],
        'RISK NEED': [1],
        'DESIGN INPUT': [2],
        'DESIGN OUTPUT SOLUTION': list(range(3, 20))
    }

"""
These functions each checks a specific aspect of an RTM field and return a ValidationResult object,
ready to be printed on the terminal as the final output of this app.
"""

# --- Standard Library Imports ------------------------------------------------
# None

# --- Third Party Imports -----------------------------------------------------
# None

# --- Intra-Package Imports ---------------------------------------------------
import rtm.validate.checks as checks
from rtm.validate.validator_output import ValidationResult
import rtm.main.context_managers as context


def val_column_exist(field_found) -> ValidationResult:
    title = "Field Exist"
    if field_found:
        score = "Pass"
        explanation = None
    else:
        score = "Error"
        explanation = "Field not found"
    return ValidationResult(score, title, explanation)


def val_column_sort(field) -> ValidationResult:
    """Does the argument field actually appear after the one it's supposed to?"""
    title = "Left/Right Order"

    field_left = checks.get_expected_field_left(field)
    if field_left is None:
        # argument field is supposed to be all the way to the left. It's always in the correct position.
        score = "Pass"
        explanation = "This field appears to the left of all the others"
    elif field_left.get_min_index_for_field_right() <= field.get_index():
        # argument field is to the right of its expected left-hand neighbor
        score = "Pass"
        explanation = (
            f"This field comes after the {field_left.get_name()} field as it should"
        )
    else:
        score = "Error"
        explanation = f"This field should come after {field_left.get_name()}"
    return ValidationResult(score, title, explanation)


def val_cells_not_empty(values) -> ValidationResult:
    title = "Not Empty"
    indices = []
    for index, value in enumerate(values):
        if checks.cell_empty(value):
            indices.append(index)
    if not indices:
        score = "Pass"
        explanation = "All cells are non-blank"
    else:
        score = "Error"
        explanation = "Action Required. The following rows are blank:"
    return ValidationResult(score, title, explanation, indices)


def val_cascade_block_not_empty():
    title = 'Not Empty'
    indices = []
    for work_item in context.work_items.get():
        position = work_item.position
        if position is None:
            indices.append(work_item.index)
    if not indices:
        score = "Pass"
        explanation = "All rows are non-blank"
    else:
        score = "Error"
        explanation = (
            "Action Required. The following rows have blank cascade blocks:"
        )
    return ValidationResult(score, title, explanation, indices)


def val_cascade_block_only_one_entry():
    title = "Single Entry"
    indices = []
    for work_item in context.work_items.get():
        _len = len(work_item.cascade_block_contents)
        if _len != 1:
            indices.append(work_item.index)
    if not indices:
        score = "Pass"
        explanation = "All rows have a single entry"
    else:
        score = "Error"
        explanation = (
            "Action Required. The following rows are blank or have multiple entries:"
        )
    return ValidationResult(score, title, explanation, indices)


def val_cascade_block_x_or_f() -> ValidationResult:
    """Value in first position must be X or F."""
    title = "X or F"

    acceptable_entries = "X F".split()

    error_indices = [
        index
        for index, work_item in enumerate(context.work_items.get())
        if not checks.dict_contains_only_acceptable_entries(
            work_item.cascade_block_contents, acceptable_entries
        )
    ]

    if not error_indices:
        score = "Pass"
        explanation = f"All entries are one of {acceptable_entries}"
    else:
        score = "Error"
        explanation = f"Action Required. The following rows contain something other than the allowed {acceptable_entries}:"
    return ValidationResult(score, title, explanation, error_indices)


def val_cascade_block_use_all_columns():

    title = "Use All Columns"

    # Setup fields
    fields = context.fields.get()
    cascade_block = fields.get_matching_field('CascadeBlock')
    subfield_count = len(cascade_block)
    positions_expected = set(range(subfield_count))

    # Setup Work Items
    work_items = context.work_items.get()
    positions_actual = set(
        work_item.cascade_block_contents.get_first_key() for
        work_item in
        work_items
    )

    missing_positions = positions_expected - positions_actual

    if len(missing_positions) == 0:
        score = "Pass"
        explanation = f"All cascade levels were used."
    else:
        score = "Warning"
        explanation = f"Some cascade levels are unused"

    return ValidationResult(score, title, explanation)


def get_row(index):
    return index + 2


# TODO: replace with something more maintainable / straightforward
cell_validation_functions = [
    globals()[name] for name in globals() if name.startswith("val_cells_")
]


# --- Cascade Level -----------------------------------------------------------

def valid_cascade_levels(field):

    title = 'Valid Entries'
    body = field.body
    error_indices = [
        index for
        index, value in
        enumerate(body) if
        not checks.cell_empty(value) and value not in checks.allowed_cascade_levels.keys()
    ]

    if not error_indices:
        score = "Pass"
        explanation = "All cell values are valid"
    else:
        score = "Error"
        explanation = f'The following cells contain values other than the allowed {checks.allowed_cascade_levels.keys()}:'
    return ValidationResult(score, title, explanation, error_indices)


def val_matching_cascade_levels():
    fields = context.fields.get()
    cascade_level = fields.get_matching_field('CascadeLevel')
    title = 'Matching Levels'
    body = cascade_level.body

    # --- Don't report on rows that failed for other reasons (i.e. blank or invalid input
    exclude_results = [
        val_cells_not_empty(body),
        valid_cascade_levels(cascade_level),
        val_cascade_block_not_empty()
    ]
    exclude_indices = []
    for result in exclude_results:
        exclude_indices += list(result.indices)
    indices_to_check = set(range(len(body))) - set(exclude_indices)

    error_indices = []
    work_items = context.work_items.get()
    for index in indices_to_check:
        cascade_block_position = work_items[index].position
        cascade_level_value = body[index]
        allowed_positions = checks.allowed_cascade_levels[cascade_level_value]
        if cascade_block_position not in allowed_positions:
            error_indices.append(index)

    if not error_indices:
        score = "Pass"
        explanation = "All rows (that passed previous checks) match the position marked in the Cascade Block"
    else:
        score = "Error"
        explanation = f'The following rows do not match the cascade position marked in the Cascade Block:'
    return ValidationResult(score, title, explanation, error_indices)


if __name__ == "__main__":
    a = 1
    b = 1
    print(a in b)
